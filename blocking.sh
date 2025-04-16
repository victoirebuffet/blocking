module load intel/2019
module load python/3.6/intel/2019

# Create an array of years from 1979 to 2023
years=($(seq 1979 2023))

# Loop over all years and submit jobs
for year in "${years[@]}"
do
    qsub -q batch -N compute_blocking_"$year" << EOF

module load intel/2019
module load python/3.6/intel/2019

# Set the 'year' environment variable
export year="$year"

# Run the Python script
python blocking_job.py
EOF
    
done