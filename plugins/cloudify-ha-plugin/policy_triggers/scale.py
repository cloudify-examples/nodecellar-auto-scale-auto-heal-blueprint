######
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

from cloudify.decorators import workflow
from cloudify.plugins import lifecycle


@workflow
def scale(ctx, node_id, delta, scale_compute, min_instances, max_instances, **_):
    graph = ctx.graph_mode()
    node = ctx.get_node(node_id)
    if not node:
        raise ValueError("Node {0} doesn't exist".format(node_id))
    if delta == 0:
        ctx.logger.info('delta parameter is 0, so no scaling will take place.')
        return
    host_node = node.host_node
    scaled_node = host_node if (scale_compute and host_node) else node
    curr_num_instances = scaled_node.number_of_instances
    if curr_num_instances == min_instances and delta < 0:
        ctx.logger.info('The current number of instances ({0}) is equal to the '
                        'minimum allowed number of instances ({1}). The custom_scale '
                        'workflow won\'t take place.'
                        .format(curr_num_instances, min_instances))
        return
    elif curr_num_instances == max_instances and delta > 0:
        ctx.logger.info('The current number of instances ({0}) is equal to the '
                        'maximum allowed number of instances ({1}). The custom_scale '
                        'workflow won\'t take place.'
                        .format(curr_num_instances, max_instances))
        return
    planned_num_instances = curr_num_instances + delta
    if planned_num_instances < 0:
        raise ValueError('Provided delta: {0} is illegal. current number of '
                         'instances of node {1} is {2}'
                         .format(delta, node_id, curr_num_instances))

    modification = ctx.deployment.start_modification({
        scaled_node.id: {
            'instances': planned_num_instances

            # These following parameters are not exposed at the moment,
            # but should be used to control which node instances get scaled in
            # (when scaling in).
            # They are mentioned here, because currently, the modification API
            # is not very documented.
            # Special care should be taken because if `scale_compute == True`
            # (which is the default), then these ids should be the compute node
            # instance ids which are not necessarily instances of the node
            # specified by `node_id`.

            # Node instances denoted by these instance ids should be *kept* if
            # possible.
            # 'removed_ids_exclude_hint': [],

            # Node instances denoted by these instance ids should be *removed*
            # if possible.
            # 'removed_ids_include_hint': []
        }
    })
    try:
        ctx.logger.info('Deployment modification started. '
                        '[modification_id={0}]'.format(modification.id))
        if delta > 0:
            added_and_related = set(modification.added.node_instances)
            added = set(i for i in added_and_related
                        if i.modification == 'added')
            related = added_and_related - added
            try:
                lifecycle.install_node_instances(
                    graph=graph,
                    node_instances=added,
                    intact_nodes=related)
            except:
                ctx.logger.error('Scale out failed, scaling back in.')
                for task in graph.tasks_iter():
                    graph.remove_task(task)
                lifecycle.uninstall_node_instances(
                    graph=graph,
                    node_instances=added,
                    intact_nodes=related)
                raise
        else:
            removed_and_related = set(modification.removed.node_instances)
            removed = set(i for i in removed_and_related
                          if i.modification == 'removed')
            related = removed_and_related - removed
            lifecycle.uninstall_node_instances(
                graph=graph,
                node_instances=removed,
                intact_nodes=related)
    except:
        ctx.logger.warn('Rolling back deployment modification. '
                        '[modification_id={0}]'.format(modification.id))
        try:
            modification.rollback()
        except:
            ctx.logger.warn('Deployment modification rollback failed. The '
                            'deployment model is most likely in some corrupted'
                            ' state.'
                            '[modification_id={0}]'.format(modification.id))
            raise
        raise
    else:
        try:
            modification.finish()
        except:
            ctx.logger.warn('Deployment modification finish failed. The '
                            'deployment model is most likely in some corrupted'
                            ' state.'
                            '[modification_id={0}]'.format(modification.id))
            raise
