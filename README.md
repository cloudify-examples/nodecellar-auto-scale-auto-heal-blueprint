# Cloudify Nodecellar Example

This is a fork of the Cloudify Nodecellar Example.

It's main purpose is to demonstrate scaling a Node JS Webserver Backend with a Node JS Frontend.

### Step 1: Upload the blueprint

`cfy blueprints upload -b <choose_blueprint_id> -p <blueprint_filename>` <br>

### Step 2: Create a deployment

Every one of these blueprints have inputs, which can be populated for a deployment using input files. <br>
Example input files are located inside the *inputs* directory. <br>
Note that these files only contain the **mandatory** inputs, i.e, one's that the blueprint does not define a default value for.

After you filled the input file corresponding to your blueprint, run: <br>

`cfy deployments create -b <blueprint_id> -d <choose_deployment_id> -i inputs/<inputs_filename>`

### Step 4: Install

Once the deployment is created, we can start running workflows: <br>

`cfy executions start -w install -d <deployment_id>`

This process will create all the cloud resources needed for the application: <br>

- VM's
- Floating IP's
- Security Groups

and everything else that is needed and declared in the blueprint.<br>

### Step 5: Verify installation

Once the workflow execution is complete, we can view the application endpoint by running: <br>

`cfy deployments outputs -d <deployment_id>`

Hit that URL to see the application running.

### Step 6: Demo the Auto Scale Example

Using the IP & PORT that are in the output of the command in Step 5, you can run:

`for i in {1..6000}; do curl http://$IP:$PORT > /dev/null; done`

Depending on the number of shells you run this command in, the application should scale the NodeJS VM with the Nodecellar application, and add nodes to HA Proxy.

### Step 7: Uninstall

Now lets run the `uninstall` workflow. This will uninstall the application,
as well as delete all related resources. <br>

`cfy executions start -w uninstall -d <deployment_id>`

### Step 8: Delete the deployment

Its best to delete deployments we are no longer using, since they take up memory on the management machine.
We do this by running:

`cfy deployments delete -d <deployment_id>`
