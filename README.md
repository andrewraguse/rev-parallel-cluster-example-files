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

#### Example 1: Single-Node Job

Navigate to the example folder and run the first example, which tests single-node functionality:

```bash
cd rev-parallel-cluster-example-files/example-1
reV generation -c AWS_test_config_generation.json
```

- **Monitor Execution**: Check `squeue` for job status and use `reV status` to confirm the job runs without issues.
- **Check Logs**: If issues occur, especially 503 errors, check the logs under `/logs/stdout/` for details.

#### Example 2: Multi-Node Job

Once single-node functionality is verified, proceed with the multi-node example:

```bash
cd ../example-2
reV pipeline config_pipeline.json --monitor
```

- **Scaling Nodes**: If only one node is active, other nodes may take time to initialize. Monitor using `squeue`.
- **Retry Failed Jobs**: If any jobs fail, re-running the command will restart any incomplete tasks.

## How to Make Changes to the Cluster

To customize your ParallelCluster configuration, there are a few key parameters and settings you can adjust, depending on your requirements. Below are the main configuration options you can modify.

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
- **option**: The execution environment, here using AWS ParallelCluster (`awspc`).
- **qos**: Quality of Service level, often `normal` for standard priority.
- **walltime**: Expected time in hours to complete the job.
- **allocation**: Specifies the cluster allocation (e.g., `revcluster`).
- **nodes**: Number of cluster nodes to use.
- **sites_per_worker**: Number of project sites processed by each worker.
- **max_workers**: Number of workers per CPU (controls parallelization).
- **timeout**: Timeout in seconds for each job or task.

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
