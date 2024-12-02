for had in {0..199}
do
    filename='random_team_'${had}'.csv'
    echo "Evaluating with file: ${had}"
    py evaluate.py $filename
done