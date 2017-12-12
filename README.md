[![CircleCI](https://circleci.com/gh/cloudify-examples/nodecellar-auto-scale-auto-heal-blueprint.svg?style=svg)](https://circleci.com/gh/cloudify-examples/nodecellar-auto-scale-auto-heal-blueprint)

# Nodecellar Auto-scale Auto-heal Blueprint

This blueprint deploys a demo wine store application that is based on Node.js and MongoDB using Cloudify.

## Prerequisites

Before you install this blueprint, you must have a *Cloudify Manager* running in either AWS, Azure, or Openstack.

The [example Cloudify environment](https://github.com/cloudify-examples/cloudify-environment-setup) README file explains how to setup a Cloudify environment that includes all of the prerequisites, including keys, plugins, and secrets.

### Step 1: Install the demo application

To install this blueprint, run the *Cloudify CLI* command for your cloud vendor. This command uploads the demo application blueprint to the manager, creates a deployment, and starts an install workflow. When the command is finished, you can access the wine store application.


#### For AWS, run:

```shell
$ cfy install \
    https://github.com/cloudify-examples/nodecellar-auto-scale-auto-heal-blueprint/archive/4.1.zip \
    -b demo \
    -n aws-blueprint.yaml
```


#### For Azure, run:

```shell
$ cfy install \
    https://github.com/cloudify-examples/nodecellar-auto-scale-auto-heal-blueprint/archive/4.1.zip \
    -b demo \
    -n azure-blueprint.yaml
```


#### For Openstack, run:

```shell
$ cfy install \
    https://github.com/cloudify-examples/nodecellar-auto-scale-auto-heal-blueprint/archive/4.1.zip \
    -b demo \
    -n openstack-blueprint.yaml
```


Here is an example of the command output:

```shell
$ cfy install \
>     https://github.com/cloudify-examples/nodecellar-auto-scale-auto-heal-blueprint/archive/4.1.zip \
>     -b demo \
>     -n aws-blueprint.yaml
Downloading https://github.com/cloudify-examples/nodecellar-auto-scale-auto-heal-blueprint/archive/4.1.zip to ...
Uploading blueprint /.../nodecellar-auto-scale-auto-heal-blueprint-4.0.1/aws-blueprint.yaml...
 aws-blueprint.yaml |##################################################| 100.0%
Blueprint uploaded. The blueprint's id is demo
Creating new deployment from blueprint demo...
Deployment created. The deployment's id is demo
Executing workflow install on deployment demo [timeout=900 seconds]
Deployment environment creation is in progress...
2017-05-01 00:00:00.000  CFY <demo> Starting 'install' workflow execution
...
...
...
2017-05-01 00:05:00.000  CFY <demo> 'install' workflow execution succeeded
```


### Step 2: Verify the demo is installed and started

After the workflow execution is finished, you can get the IP address of the application endpoint by running: <br>

```shell
$ cfy deployments outputs demo
```

Here is an example of the command output:

```shell
Retrieving outputs for deployment demo...
 - "endpoint":
     Description: Web application endpoint
     Value: http://10.239.0.18:8080/
```

Enter the URL from the endpoint value in your web browser to access the wine store application.


### Step 3: Simulate Auto-scaling

Run a benchmarking command to simulate auto-scaling.

```shell
$ ab -n 1000000 -c 200 http://10.239.0.18:8080/ # insert your URL instead of this one.
```

This command increases the number of requests to the application. As a result, the CPU used by the node process on the nodejs_host VMs rises above the scale up threshold. The Diamond plugin monitors this metric, and the Riemann auto-scale policy calls the scale workflow trigger.

If you kill this command, expect that the CPU drops below the scale down threshold, and the application scales down.

_Note: This auto-scaling example assumes that the VM is an appropriate flavor for the benchmarking tool to challenge the VM's resources. This configuration above is based on the t2.micro AWS instance._

There are many ways to verify auto-scaling. If you have Cloudify Premium, you can view the executions in the Cloudify Manager web interface.
You can also run `cfy executions list` for a CLI view:

```shell
$ cfy executions list
Listing all executions...

Executions:
+--------------------------------------+-------------------------------+------------+---------------+--------------------------+-------+------------+----------------+------------+
|                  id                  |          workflow_id          |   status   | deployment_id |        created_at        | error | permission |  tenant_name   | created_by |
+--------------------------------------+-------------------------------+------------+---------------+--------------------------+-------+------------+----------------+------------+
| 10e5a704-6c97-43f0-bf84-cb3c3b5cf9e5 | create_deployment_environment | terminated |      demo     | 2017-05-01 00:00:00.000  |       |  creator   | default_tenant |   admin    |
| a1dcbc8f-ae02-4fc7-80a6-1201a706b72b |            install            | terminated |      demo     | 2017-05-01 00:00:00.000  |       |  creator   | default_tenant |   admin    |
| 53d9c07e-7340-4860-91c5-d402877be341 |             scale             | terminated |      demo     | 2017-05-01 00:05:00.000  |       |  creator   | default_tenant |   admin    |
| 2dd15f7b-78ed-46db-9084-de8d0345ff3e |             scale             |  started   |      demo     | 2017-05-01 00:10:00.000  |       |  creator   | default_tenant |   admin    |
+--------------------------------------+-------------------------------+------------+---------------+--------------------------+-------+------------+----------------+------------+
```

### Step 3: Simulate Auto-healing

You can stop or suspend a running nodejs_host to simulate a VMfailed host. The Riemann failed host policy recognizes the lack of system CPU metrics reporting on the host and triggers the heal workflow.


### Step 4: Uninstall the demo application

To uninstall the nodecellar application, run the `uninstall` workflow. This removes the application and deletes all of the related resources. <br>

```shell
$ cfy uninstall --allow-custom-parameters -p ignore_failure=true demo
```
