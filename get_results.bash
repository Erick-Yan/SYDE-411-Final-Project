# Loop through weight values (from 0.0 to 1.0 in steps of 0.01)
# for weight in 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
# do
#     # Run the optimization script with constraints
#     echo "Optimizing with weight: $weight"
#     py pulp_optimizer.py $weight
# done

# Loop through the same weight values for evaluation
for weight in 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
do
    # Construct filenames for the optimized teams
    file0="v2team_=${weight}.csv"

    # Run the evaluation script for the team
    echo "Evaluating with weight: $weight"
    py evaluate.py $file0
done
