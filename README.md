## Running the Examples from a ParallelCluster Head Node

### 1. SSH into the Head Node

To access the ParallelCluster’s head node, use the SSH command below with your private key and the head node’s public IP:

```bash
ssh -i ~/.ssh/id_rsa ec2-user@<head-node-ip-address>
```

- _Finding the Head Node IP_: In the AWS Console, navigate to **EC2**, locate your head node, and copy its public IP address.
- Once connected, continue with the following commands to set up the environment.

### 2. Install Miniconda on the Head Node

We’ll install Miniconda to manage Python dependencies:

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh Miniconda3-latest-Linux-x86_64.sh
```

- **Note**: During installation, press `Enter` to proceed, then type `yes` when prompted.
- After installation, activate the Miniconda environment:

```bash
source ~/.bashrc
```

### 3. Set Up the reV Environment

Now we’ll create a Python environment specifically for reV and install the necessary packages:

```bash
conda create --name rev python=3.9
conda activate rev
pip install NREL-reV
git clone https://github.com/switchbox-data/rev-parallel-cluster-example-files.git
```

### 4. Run a Simple SLURM Command to Verify Setup

To verify that SLURM and the environment are set up correctly, we’ll run a simple SLURM job:

```bash
echo -e '#!/bin/bash\nsleep 30\necho "Hello World from $(hostname)"' > my_script.sh
chmod +x my_script.sh
sbatch my_script.sh
```

After submitting the job, check the SLURM controller status:

```bash
sudo systemctl status slurmctld
```

- **Monitor the Job**: Use `squeue` to check job status. If auto-provisioning is enabled, the job will remain in the `CF` (configuring) state until nodes are provisioned. Once running, the status changes to `R`.

### 5. Running the reV Example Jobs

Here’s an enhanced version of the examples with more details about the data size and expected performance:

---

### Example 1: Single-Node Job (Small Data Load)

This example demonstrates `reV` functionality with a small dataset, designed to run quickly on a single node. This setup is ideal for initial testing or when analyzing fewer than 10 GIDs, as it completes relatively fast.

1. **Navigate to the Example Folder**:
   ```bash
   cd rev-parallel-cluster-example-files/example-1
   ```

2. **Run the Single-Node Job**:
   Execute the command:
   ```bash
   reV generation -c AWS_test_config_generation.json
   ```

3. **Monitor Execution**:
   - Use `squeue` to check the job status on the cluster.
   - Run `reV status` to confirm the job is progressing without issues.

4. **Check Logs**:
   - If any issues arise, such as 503 errors or connection timeouts, inspect the logs in `/logs/stdout/` for detailed error messages.

   **Note**: This configuration, processing fewer than 10 GIDs, should complete relatively quickly (under a minute) as it only requires a single node and minimal compute resources.

---

### Example 2: Multi-Node Job (Large Data Load with Sequential Pipeline Execution)

In this example, `reV` processes **2,500 GIDs** across multiple nodes, using `reV pipeline` to execute multiple steps in sequence. The `--monitor` flag is crucial here, as it ensures that each pipeline step (e.g., `generation`, `collect`, `multi-year`) runs in the correct order, with dependent steps starting immediately after the previous step completes. Without `--monitor`, subsequent steps would not initiate, making it impossible to proceed through the full pipeline.

1. **Navigate to the Example Folder**:
   ```bash
   cd rev-parallel-cluster-example-files/example-2
   ```

2. **Run the Multi-Node Job with Sequential Pipeline Execution**:
   Use the `--monitor` flag to ensure that dependent steps run in the intended sequence:
   ```bash
   reV pipeline config_pipeline.json --monitor
   ```

   - The `--monitor` flag enables dependent steps, such as `collect` and `multi-year`, to begin processing as soon as the preceding step (like `generation`) completes.
   - Without `--monitor`, each stage would wait indefinitely, preventing the pipeline from progressing.

3. **Scaling Nodes**:
   - Given the large data load (2,500 GIDs), the job will scale across multiple nodes to distribute the workload.
   - Use `squeue` to monitor node activity and ensure resources are utilized effectively.

4. **Retrying Failed Jobs**:
   - If any job fails, re-running `reV pipeline` with `--monitor` will restart only the incomplete stages, ensuring continuity without redundant processing.

5. **Performance Considerations**:
   - Processing 2,500 GIDs across dependent steps is optimized by the `--monitor` option, enabling each stage to run sequentially without delay.
   - **Tip**: To further optimize performance, consider adjusting the node count based on data size.

   ### Example 3: Batch Processing for Multi-Year Analysis

   In this example, we use `reV` batch mode to analyze **17,000 GIDs over two years**. Initially, it was thought that batch processing would execute each year sequentially. However, further investigation showed that batch processing split the resources, allocating half the nodes to each year, causing each job to use only half the available nodes. This configuration effectively doubled the runtime, as both years ran concurrently on a reduced number of nodes.

   Despite the doubled runtime, we found that by adjusting the `sites_per_worker` parameter to a lower value (10), we reduced the risk of CPU overload, allowing the jobs to run efficiently without overloading the compute resources.

   #### Objective

   To analyze:
   - **17,000 GIDs** (geospatial locations).
   - **Two years** of data (2011 and 2012).

   This setup enables the system to handle a large data load by reducing the intensity of parallelization. However, since batch processing does not enforce sequential execution, each job may still share the allocated resources.

   #### Findings from Batch Mode

   - **CPU Utilization**: Setting `sites_per_worker` to a lower value helped limit CPU usage, preventing the CPU from maxing out even when both years were processed concurrently.
   - **Execution Time**: Since batch mode does not enforce sequential execution, each year’s job used only half the nodes, effectively doubling the runtime compared to using all nodes for a single year.
   - **Scaling with Data Size**: Increasing data size requires scaling the number of nodes. Lowering `sites_per_worker` is an effective way to control resource usage, but may still necessitate additional nodes if data volume exceeds current capacity.

   #### Configuration Details

   - **Batch Configuration**: The batch file splits the task by year, with 8 nodes automatically allocated to each year by SLURM.
   - **Execution Control**:
     - **16 Nodes**: Using 16 nodes allows each year to utilize 8 nodes concurrently.
     - **Parallelization Parameters**:
       - **`sites_per_worker`**: Set to 10 to reduce the load per worker, avoiding CPU overload.
       - **`max_workers`**: Set to 1 to control the level of concurrency within each worker.

   #### Example Execution Steps

   1. **Navigate to the Example Folder**:
      ```bash
      cd rev-parallel-cluster-example-files/example-3
      ```

   2. **Run the Batch Job**:
      Execute the batch job with:
      ```bash
      reV batch -c config_batch.json
      ```

   3. **Monitor Execution**:
      - Check `squeue` to observe how SLURM allocates nodes between the years.
      - Use `reV status` to track the progression and see that both years are processed concurrently on separate node groups.

   4. **Check Logs**:
      - If issues such as CPU overload occur, inspect logs in `year-2011/logs/stdout/` or `year-2012/logs/stdout/`.
      - If needed, consider increasing nodes or lowering `sites_per_worker` to reduce CPU load further.

   #### Key Takeaways

   - **Batch Mode and Parallelism**: Batch processing itself does not enforce sequential processing. Instead, it may split resources between jobs, which can lead to each job using only a subset of the allocated nodes.
   - **Reducing Sites per Worker**: Lowering `sites_per_worker` effectively reduces CPU demand, allowing the job to run with less intensive resource usage. However, this may extend the runtime, as each worker processes fewer sites concurrently.
   - **Scaling Recommendations**: For very large datasets, you may still need to increase node count to meet resource requirements, especially if batch mode splits resources across jobs.

#### Observations and Recommendations

- **Scaling Requirements**: As data volume increases, adding nodes (or vCPUs) becomes essential. With `reV`’s current design, the data load is proportionally distributed across available nodes. For a target use case, such as analyzing 10 years of data for 17,000 GIDs, we recommend scaling up nodes incrementally.
- **Sequential Execution Workaround**: If a team prefers to limit the number of EC2 instances in use (e.g., only 4 instances at a time), a good approach is to **manually batch jobs** by year or GID subsets.

### Example 4: Sequential Multi-Year Analysis with `reV pipeline`

In this example, we use `reV pipeline` with a configuration that runs multiple jobs sequentially, processing a large dataset year by year. This approach is effective for handling extensive data across multiple years without overloading compute resources. By running each year independently and sequentially, you can control the resource load on your nodes, making it suitable for situations where limited compute resources are available.

#### Objective

To process:
- **Data from multiple years** sequentially (2007, 2008, 2009).
- **Multi-year analysis** on the collected data after each individual year has been processed.

This setup effectively distributes the workload across time and minimizes resource strain, as each job uses a defined subset of resources, preventing CPU overload.

#### Pipeline Configuration

The configuration below splits data processing for each year into separate `generation` steps, which are executed sequentially, followed by a `multi-year` step for aggregating results across the years.

```json
{
  "logging": {
    "log_file": "./logs/pipeline.log",
    "log_level": "DEBUG"
  },
  "pipeline": [
    {
      "command": "generation",
      "generation_2007": "./config_gen1.json"
    },
    {
      "command": "generation",
      "generation_2008": "./config_gen2.json"
    },
    {
      "command": "generation",
      "generation_2009": "./config_gen3.json"
    },
    {
      "multi-year": "./config_multi-year.json"
    }
  ]
}
```

**Explanation**:
- Each `generation` command processes data for a specific year, with unique configurations for 2007, 2008, and 2009.
- Once all `generation` steps are complete, the `multi-year` step performs analysis across the combined data.

This configuration allows each year to be processed independently, reducing CPU load by processing fewer sites per job and ensuring a controlled use of resources.

#### Execution Instructions

1. **Save the Configuration File**:
   Save the pipeline configuration as `config_pipeline.json`.

2. **Run the Pipeline Command**:
   To start the pipeline, execute the following command with `--monitor` to manage sequential execution:
   ```bash
   reV pipeline -c config_pipeline.json --monitor
   ```

3. **Explanation of the Command**:
   - **`reV pipeline -c config_pipeline.json`**: Specifies the pipeline configuration file.
   - **`--monitor`**: Ensures that each step waits for the previous one to complete before starting the next. This flag is essential for sequential execution, particularly for steps like `multi-year` that depend on the completion of previous years.

4. **Monitor Execution**:
   - Use `squeue` to observe job status on SLURM.
   - Run `reV status` to track the pipeline’s progress and verify that each stage runs in sequence.

5. **Check Logs**:
   - Check the `./logs/pipeline.log` file for detailed information on each step’s execution.
   - If you encounter issues (e.g., CPU overload or memory constraints), consider lowering the `sites_per_worker` parameter in the `generation` configurations or increasing node resources.

#### Key Takeaways

- **Sequential Processing**: This configuration ensures that each year is processed in sequence, avoiding overload and optimizing resource allocation.
- **Efficient Resource Management**: By processing fewer sites per worker and controlling node usage, this setup helps manage large datasets without maxing out compute capacity.
- **Scalability**: This approach is easily scalable; to add more years, simply duplicate the `generation` configuration with updated file paths and year parameters.

## Running reV Commands

### **reV Configurations**

#### **Summary**
Configuration files are the foundation of `reV` commands, defining resources, settings, and parameters. These files are in JSON, JSON5, YAML, or TOML formats and are essential for specifying inputs, outputs, and processing details.

#### **Examples**
Each command example section below includes a link to configuration files used with that command.

---

### **reV Pipeline**

#### **Summary**
`reV pipeline` runs a series of jobs in sequence, like `generation`, `collect`, and `aggregation`, according to a predefined order in the configuration. Each step is executed one at a time, allowing users to automate an end-to-end workflow.

#### **Sample Command**
```bash
reV pipeline -c config_pipeline.json --monitor
```

#### **Examples**
- [Pipeline Documentation](https://nrel.github.io/reV/_cli/reV%20pipeline.html)
- [Sample Config File](https://github.com/NREL/ReEDS-2.0/blob/main/inputs/supply_curve/metadata/wind-ons_limited_ba/config_pipeline.json5)


#### **Pipeline/Configuration Tips**
- **Sequential Execution**: Set each analysis step to run one after the other.
- **Execution Monitoring**: Add `--monitor` to let `reV` check for completion and progress in real-time.
- **Batch Processing**: To run a `pipeline` with multiple configurations, consider using `reV batch` instead.
- **Collection Pattern**: Set `collect_pattern` to `"PIPELINE"` in configuration files to ensure that `reV collect` gathers outputs from each step in the pipeline automatically.

---

### **reV Batch**

#### **Summary**
`reV batch` runs a pipeline with multiple configurations, allowing users to test variations by running the same pipeline across different scenarios.

#### **Sample Command**
```bash
reV batch -c config_batch.json --monitor
```

#### **Examples**
- [Batch Documentation](https://nrel.github.io/reV/_cli/reV%20batch.html)
- [Sample Config File](https://github.com/NREL/ReEDS-2.0/blob/main/inputs/supply_curve/metadata/egs_reference/config_batch.json)

#### **Pipeline/Configuration Tips**
- **Use for Multiple Configurations**: Ideal for running the same pipeline across different parameter sets.
- **Unique Set Tags**: Ensure each configuration variation has a unique `set_tag` to avoid confusion.

---

### **reV Generation**

#### **Summary**
`reV generation` calculates renewable energy production by simulating energy generation at individual sites or across areas using SAM (System Advisor Model) configurations. It pulls data from renewable resources (like wind or solar) and outputs energy estimates.

#### **Sample Command**
```bash
reV generation -c config_gen.json
```

#### **Examples**
- [Generation Documentation](https://nrel.github.io/reV/_cli/reV%20generation.html)
- [Sample Config File](https://github.com/NREL/reV/blob/main/examples/full_pipeline_execution/config_gen.json)

#### **Execution Control Settings**
Here’s an example of an `execution_control` block commonly used with `reV generation`:
```json
"execution_control": {
    "option": "awspc",
    "qos": "normal",
    "walltime": 1,
    "allocation": "revcluster",
    "nodes": 16,
    "sites_per_worker": 20,
    "max_workers": 1,
    "timeout": 1800
}
```
- **option**: Specifies the execution environment, using AWS ParallelCluster (`awspc`) in this case.
- **qos**: Quality of Service level, typically set to `normal` for standard priority.
- **walltime**: Expected duration in hours for the job to complete.
- **allocation**: Defines the cluster allocation (e.g., `revcluster`).
- **nodes**: Maximum number of **vCPUs** to use for the job. SLURM will automatically provision the required number of nodes based on this value. Each compute instance in this cluster uses a `c5.xlarge` instance type, which has 4 vCPUs. Therefore, specifying `16 nodes` would provision 4 EC2 instances.
- **`sites_per_worker`**: Specifies the number of project sites each worker processes in parallel. Lowering this number reduces the level of parallel computation, which can be useful for managing resource usage. For example, setting `sites_per_worker` to 10 will result in a slower job execution but will help prevent overuse of compute resources by reducing the load on each worker. Tinkering with `sites_per_worker` in combination with the number of `nodes` will be essential for determining the optimal amount of compute resources your job requires. Adjusting both settings allows you to balance execution time with resource utilization, helping to fine-tune the efficiency and performance of your workload.
- **max_workers**: Number of workers per vCPU, controlling the level of parallelization within each node.
- **timeout**: Timeout in seconds for each job or task before it is marked as failed.

---

### **reV Bespoke**

#### **Summary**
`reV bespoke` performs layout optimization for wind projects by adjusting turbine placement for maximum efficiency or minimal cost per grid point. It provides a detailed, location-specific analysis for wind projects.

#### **Sample Command**
```bash
reV bespoke -c config_bespoke.json
```

#### **Examples**
- [Bespoke Documentation](https://nrel.github.io/reV/_cli/reV%20bespoke.html)
- [Sample Config File](https://github.com/NREL/ReEDS-2.0/blob/main/inputs/supply_curve/metadata/wind-ons_open_ba/config_bespoke.json5)

#### **Pipeline/Configuration Tips**
- For wind projects requiring individual grid point optimization, use `reV bespoke`.

---

### **reV Econ**

#### **Summary**
`reV econ` calculates the financial performance of renewable energy projects, such as Levelized Cost of Energy (LCOE), by analyzing project and maintenance costs and revenue data.

#### **Sample Command**
```bash
reV econ -c config_econ.json --monitor
```

#### **Examples**
- [Econ Documentation](https://nrel.github.io/reV/_cli/reV%20econ.html)
- [Sample Config File](https://github.com/NREL/reV/blob/main/examples/advanced_econ_modeling/config_econ.json)

#### **Pipeline/Configuration Tips**
- Typically follows `generation` in the pipeline.
- Requires project cost and revenue data.

---

### **reV Collect**

#### **Summary**
`reV collect` gathers data from multiple nodes or outputs, merging it into a single HDF5 file, which simplifies data analysis by consolidating distributed data into one file.

#### **Sample Command**
```bash
reV collect -c config_collect.json --monitor
```

#### **Examples**
- [Collect Documentation](https://nrel.github.io/reV/_cli/reV%20collect.html)
- [Sample Config File](https://github.com/NREL/reV/blob/main/examples/aws_pcluster/config_collect.json)

#### **Pipeline/Configuration Tips**
- Set `collect_pattern` and `source_files` to `PIPELINE` for automatic integration.
- Ideal for use within a pipeline to centralize outputs.

---

### **reV Multi-Year**

#### **Summary**
`reV multi-year` aggregates data from multiple years of simulation, helping analyze long-term renewable energy production trends by combining data from multiple yearly outputs.

#### **Sample Command**
```bash
reV multi-year -c config_multi_year.json --monitor
```

#### **Examples**
- [Multi-Year Documentation](https://nrel.github.io/reV/_cli/reV%20multi-year.html)
- [Sample Config File](https://github.com/NREL/reV/blob/main/examples/aws_pcluster/config_multi-year.json)

#### **Pipeline/Configuration Tips**
- Use `PIPELINE` paths to ensure continuous execution in a multi-step pipeline.
- Best used for long-term trend analysis across multiple data years.

---

### **reV Supply-Curve-Aggregation and Supply-Curve**

#### **Summary**
These commands aggregate and analyze energy supply data across grid points. `Supply-Curve-Aggregation` consolidates data, while `Supply-Curve` performs economic and capacity assessments for grid-based renewable sites.

#### **Sample Command**
```bash
reV supply-curve -c config_supply_curve.json --monitor
```

#### **Examples**
- [Supply Curve Aggregation Documentation](https://nrel.github.io/reV/_cli/reV%20supply-curve-aggregation.html)
- [Supply Curve Documentation](https://nrel.github.io/reV/_cli/reV%20supply-curve.html)

#### **Pipeline/Configuration Tips**
- `collect_pattern`: Set to `PIPELINE` for streamlined integration.
- Use these commands in sequence for optimal grid-wide assessment.

---

### **Additional Components (e.g., rep-profiles, hybrids, nrwal, qa-qc, script, status)**

Each of these commands has unique applications, from `rep-profiles` for representative profile generation to `nrwal` for lifecycle assessments, `qa-qc` for quality checks, and `script` for custom scripts.

For each of these:

- **Summary**: Tailor based on specific functionality, such as quality checks or profile generation.
- **Sample Command**: Follow a consistent format:
  ```bash
  reV <command> -c config_<command>.json --monitor
  ```

For detailed uses, see each command’s documentation:

- **rep-profiles**: [Documentation](https://nrel.github.io/reV/_cli/reV%20rep-profiles.html)
- **hybrids**: [Documentation](https://nrel.github.io/reV/_cli/reV%20hybrids.html)
- **nrwal**: [Documentation](https://nrel.github.io/reV/_cli/reV%20nrwal.html)
- **qa-qc**: [Documentation](https://nrel.github.io/reV/_cli/reV%20qa-qc.html)

---

### **Project Points, Resource Files, and SAM Files**

- **Project Points**: These are specific locations or grid points analyzed within the reV framework. They can be generated using site data and selected based on project requirements.

- **Resource Files**: Resource files contain renewable energy data, like
wind speeds or solar irradiance, usually from datasets like the NREL Weather Toolkit (WTK).

- **SAM Files**: SAM (System Advisor Model) files include settings for simulating energy production, such as solar panel configuration or wind turbine specs.
