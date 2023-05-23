#!/bin/bash

echo "Please enter COMET_ML_API_KEY:"
read COMET_ML_API_KEY
export COMET_ML_API_KEY=$COMET_ML_API_KEY

echo "Please enter CEREBRIUM_API_KEY:"
read CEREBRIUM_API_KEY
export CEREBRIUM_API_KEY=$CEREBRIUM_API_KEY

echo "Variables set as environment variables"