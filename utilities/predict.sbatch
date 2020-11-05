#!/bin/bash
#SBATCH --job-name=predict_crops   # Job name
#SBATCH --mail-type=END               # Mail events
#SBATCH --mail-user=benweinstein2010@gmail.com  # Where to send mail
#SBATCH --account=ewhite
#SBATCH --cpus-per-task=1
#SBATCH --mem=30GB
#SBATCH --time=72:00:00       #Time limit hrs:min:sec
#SBATCH --output=/home/b.weinstein/logs/crops_%j.out   # Standard output and error log
#SBATCH --error=/home/b.weinstein/logs/crops_%j.err
#SBATCH --partition=gpu
#SBATCH --gpus=1

module load tensorflow/1.14.0

export PATH=${PATH}:/home/b.weinstein/miniconda3/envs/DeepTreeAttention_DeepForest/bin/:/home/b.weinstein/DeepTreeAttention/
export PYTHONPATH=/home/b.weinstein/miniconda3/envs/DeepTreeAttention_DeepForest/lib/python3.7/site-packages/:/home/b.weinstein/DeepTreeAttention/:${PYTHONPATH}
export LD_LIBRARY_PATH=/home/b.weinstein/miniconda3/envs/DeepTreeAttention_DeepForest/lib/:${LD_LIBRARY_PATH}

#Generate only once using DeepForest requires less than tensorflow 2.0
python predict_crops.py