# Node decommissioning

The procedure follows is the same as described as follows on [Cloudera](https://docs.cloudera.com/HDPDocuments/HDP3/HDP-3.1.4/administration/content/decommissioning-slave-nodes.html).

Check Application, Nodemanager and Datanode statuses before starting a decomissioning process by executing the playbook `hadoop-component-decommissioning-check.yml`. This same playbook can be run several times after the decommissioning process has begun to see its status.

To see which application is running on which node execute the command inside a node with yarn client `yarn app -status <application-id>`.

## Yarn Nodemanager decommissioning

Set the hostnames of the Nodemanagers to start to decommission in `yarn_nodemanagers_decommission` of the `excuded_nodes.yml` file seperated by comma in the Yarn tdp_variables, then set the timeout for the graceful decommissioning. The node is decommissioned once all applications running on it have terminated or after timeout and in this case it is restarted on another node. The value `-1` handles infinite timeout. Then execute the playbook `hadoop-components-decommissioning/yarn_resourcemanager_decomm_nodemanager.yml`.

## HDFS Datanode decommissioning

Set the hostnames of the Datanodes to start to decommission in `hdfs_datanodes_decommission` of the `excuded_nodes.yml` file seperated by comma in the HDFS tdp_variables, then execute the playbook `hadoop-components-decommissioning/hdfs_namenode_decomm_datanode.yml`.

*NB*: the decommissioning of the HDFS datanode can take several hours depending on the size of the file system.

## Hadoop decommissioning

The playbook `hadoop-decommissioning.yml` executes both playbooks above and starts decommissioning the Yarn Nodemanager and the HDFS Datanode. It also before executes the `yarn_capacity_scheduler.yml` playbook to reconfigure the Yarn capacity scheduler.

## Recommissioning a node

For HDFS, just delete the node from `hdfs_datanodes_decommission` and execute the playbook `hadoop-components-decommissioning/hdfs_namenode_decomm_datanode.yml`.

Concerning Yarn, delete the node from `yarn_nodemanagers_decommission`, execute the playbook `hadoop-components-decommissioning/yarn_resourcemanager_decomm_nodemanager.yml`, then restart the decommissioned Nodemanger with the playbook `yarn_nodemanager_restart.yml` and finally execute the same playbook `hadoop-components-decommissioning/yarn_resourcemanager_decomm_nodemanager.yml` again.
