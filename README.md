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
git clone https://github.com/andrewraguse/rev-parallel-cluster-example-files
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
