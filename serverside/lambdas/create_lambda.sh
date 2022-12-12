#!/bin/bash

echo "Please enter file name of lambda function: (Do not provide the .py I will add it for you :)"
read lambda_file_name
echo "- Given lambda file name:$lambda_file_name"
echo Sourcing the Env Veriables ...
source ../../.env

if [ -f "./$lambda_file_name/$lambda_file_name.py" ]; then
    echo "======"
    echo "Lambda function with the same name exist! Can not create a new one. Please provide some other name."
    echo "Exiting Shell"
    echo "======"
    exit 1
else
    echo "- Createing new lambda function template with name $lambda_file_name.py at $(pwd)/$lambda_file_name"
fi

echo "Creating the requirements.txt file. Consider deleting the file if not needed..."
mkdir $lambda_file_name && touch $lambda_file_name/requirements.txt

echo Copying all template files...
cp -r templates/microkit $lambda_file_name/microkit
cp templates/deploykit.py $lambda_file_name/deploykit.py
cp templates/domainmodel.py $lambda_file_name/domainmodel.py

cp -r templates/tests $lambda_file_name/tests
cp templates/format.sh $lambda_file_name/format.sh
cp templates/requirements_dev.txt $lambda_file_name/requirements_dev.txt

cp templates/nb-deploy-template.ipynb $lambda_file_name/nb-deploy-$(echo $lambda_file_name | tr '_' '-').ipynb
cp templates/nb-dev-template.ipynb $lambda_file_name/nb-dev-$(echo $lambda_file_name | tr '_' '-').ipynb
cp templates/nb-pytest-template.ipynb $lambda_file_name/nb-pytest-$(echo $lambda_file_name | tr '_' '-').ipynb

# echo Creating main handler py file with name $lambda_file_name.py
# touch $lambda_file_name/$lambda_file_name.py


echo Creating the build script default file ...
cat << EOF >> $lambda_file_name/build.sh
#!/bin/bash

jupyter nbconvert --to script nb-dev-$(echo $lambda_file_name | tr '_' '-').ipynb
mv nb-dev-$(echo $lambda_file_name | tr '_' '-').py $lambda_file_name.py
echo creating pyfile: $lambda_file_name.py
EOF

chmod a+x $lambda_file_name/build.sh