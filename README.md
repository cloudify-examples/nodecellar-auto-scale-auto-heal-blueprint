[![CircleCI](https://circleci.com/gh/cloudify-examples/nodecellar-auto-scale-auto-heal-blueprint.svg?style=svg)](https://circleci.com/gh/cloudify-examples/nodecellar-auto-scale-auto-heal-blueprint)

# Nodecellar Auto-scale Auto-heal Blueprint

This blueprint deploys a demo wine store application that is based on nodejs and mongodb using Cloudify.

## Compatibility

Tested with:
  * Cloudify 4.2

## Pre-installation steps

Upload the required plugins:

  * [Openstack Plugin](https://github.com/cloudify-cosmo/cloudify-openstack-plugin/releases).
  * [AWSSDK Plugin](https://github.com/cloudify-incubator/cloudify-awssdk-plugin/releases).
  * [AWS Plugin](https://github.com/cloudify-cosmo/cloudify-aws-plugin/releases).
  * [GCP Plugin](https://github.com/cloudify-incubator/cloudify-gcp-plugin/releases).
  * [Azure Plugin](https://github.com/cloudify-incubator/cloudify-azure-plugin/releases).
  * [Utilities Plugin](https://github.com/cloudify-incubator/cloudify-utilities-plugin/releases).
  * [Diamond Plugin](https://github.com/cloudify-cosmo/cloudify-diamond-plugin/releases).

_Check the blueprint for the latest version of the plugin._

Install the relevant example network blueprint for the IaaS that you wish to deploy on:

  * [Openstack Example Network](https://github.com/cloudify-examples/openstack-example-network)
  * [AWS Example Network](https://github.com/cloudify-examples/aws-example-network)
  * [GCP Example Network](https://github.com/cloudify-examples/gcp-example-network)
  * [Azure Example Network](https://github.com/cloudify-examples/azure-example-network)

## Installation

On your Cloudify Manager, navigate to `Local Blueprints` select `Upload`.

[Right-click and copy URL](https://github.com/cloudify-examples/nodecellar-auto-scale-auto-heal-blueprint/archive/master.zip). Paste the URL where it says `Enter blueprint url`. Provide a blueprint name, such as `nodecellar` in the field labeled `blueprint name`.

Select the blueprint for the relevant IaaS you wish to deploy on, for example `openstack.yaml` from `Blueprint filename` menu. Click `Upload`.

After the new blueprint has been created, click the `Deploy` button.

Navigate to `Deployments`, find your new deployment, select `Install` from the `workflow`'s menu. At this stage, you may provide your own values for any of the default `deployment inputs`.


## Deployment Outputs

Once the workflow execution is complete, we can view the application endpoint by running: <br>

```shell
$ cfy deployments outputs nodecellar
```

You should see an output like this:

```shell
Retrieving outputs for deployment nodecellar...
 - "endpoint":
     Description: Web application endpoint
     Value: http://10.239.0.18:8080/
```

Use the URL from the endpoint output and visit that URL in a browser. Play with the wine store application.


## Autoscaling

Execute a benchmarking command line application to simulate an auto-scaling scenario.

```shell
$ ab -n 1000000 -c 200 http://10.239.0.18:8080/ # insert your URL instead of this one.
```

This will increase the number of requests to the application. As a result the CPU used by the node process on the nodejs_host VMs will spike above the scale up threshold. This metric is monitored by the Diamond plugin, and the Riemann auto-scale policy calls the scale workflow trigger.

Killing this command should cause the CPU to drop below the scale down threshold, and the application will scale down.

_Note: this assumes that the VM is an appropriate flavor for the benchmarking tool to sufficiently challenge the VM. This particular configuration is with a t2.micro AWS instance._

There are a number of ways to verify the scaling. If you have Cloudify Premium,  you will see the executions in Cloudify's UI.
You can also execute `cfy executions list` for a CLI view:

```shell
$ cfy executions list
Listing all executions...

Executions:
+--------------------------------------+-------------------------------+------------+---------------+--------------------------+-------+------------+----------------+------------+
|                  id                  |          workflow_id          |   status   | deployment_id |        created_at        | error | permission |  tenant_name   | created_by |
+--------------------------------------+-------------------------------+------------+---------------+--------------------------+-------+------------+----------------+------------+
| 10e5a704-6c97-43f0-bf84-cb3c3b5cf9e5 | create_deployment_environment | terminated |      nodecellar     | 2017-05-01 00:00:00.000  |       |  creator   | default_tenant |   admin    |
| a1dcbc8f-ae02-4fc7-80a6-1201a706b72b |            install            | terminated |      nodecellar     | 2017-05-01 00:00:00.000  |       |  creator   | default_tenant |   admin    |
| 53d9c07e-7340-4860-91c5-d402877be341 |             scale             | terminated |      nodecellar     | 2017-05-01 00:05:00.000  |       |  creator   | default_tenant |   admin    |
| 2dd15f7b-78ed-46db-9084-de8d0345ff3e |             scale             |  started   |      nodecellar     | 2017-05-01 00:10:00.000  |       |  creator   | default_tenant |   admin    |
+--------------------------------------+-------------------------------+------------+---------------+--------------------------+-------+------------+----------------+------------+
```

## Simulate auto-healing

You can simulate a failed host by stopping or suspending a running nodejs_host VM. The Riemann failed host policy will recognize the lack of system cpu metrics reporting on the host and will trigger the heal workflow.


## Uninstallation

Navigate to the deployment and select `Uninstall`. When the uninstall workflow is finished, select `Delete deployment`.

```shell
$ cfy uninstall --allow-custom-parameters -p ignore_failure=true nodecellar
```
