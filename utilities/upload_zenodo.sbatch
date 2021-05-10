#!/bin/bash
#SBATCH --job-name=Upload   # Job name
#SBATCH --mail-type=END               # Mail events
#SBATCH --mail-user=benweinstein2010@gmail.com  # Where to send mail
#SBATCH --account=ewhite
#SBATCH --nodes=1                 # Number of MPI ranks
#SBATCH --cpus-per-task=1
#SBATCH --mem=40GB
#SBATCH --time=72:00:00       #Time limit hrs:min:sec
#SBATCH --output=/home/b.weinstein/logs/upload_%j.out   # Standard output and error log
#SBATCH --error=/home/b.weinstein/logs/upload_%j.err

source activate Zooniverse_pytorch
source zenodo_token
python upload_training_tiles.py