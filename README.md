<div align="center">
    <h2>A Hands-on Tutorial</h2>
    <h1>Train and Deploy a real-time ML model</h1>
    <i><a href="https://www.comet.com/site/">CometML</a></i> + <i><a href="https://www.cerebrium.ai/">Cerebrium</a></i> = 🚀
</div>
<br />
<p align="center">
  <img src="images/header.jpg" width='600' />
</p>

<br />


#### Contents
- [The problem](#the-problem)
- [Run the whole thing in 5 steps](#run-the-whole-thing-in-5-steps)
- [Lectures](#lectures)
    - [1. Model training](#1-model-training)
    - [2. Model deployment as REST API](#2-model-deployment-as-rest-api)
    - [3. Test API endpoint](#3-test-api-endpoint)

- [Next steps](#next-steps)

## The problem
Training models inside notebooks is easy. Unfortunately, this is not enough when you want to build **complete** ML solutions for real-world problems.

In this hands-on tutorial you will learn how to
- **train** an ML model that predicts crypto prices, and
- **deploy** this model as a REST API

We will use Serverless ML tools to
- track experiment runs and publish our best model to the registy, with CometML.
- deploy the model as a REST API, with Cerebrium.

Without further ado, let's get to work!

## Run the whole thing in 7 steps

1. Create a Python virtual environment with all project dependencies with

    ```
    $ make init
    ```


2. Set your API keys for [CometML]() and [Cerebrium]() in `set_environment_variables_template.sh`, rename the file and run (you can skip `CEREBRIUM_ENDPOINT_URL` for now)
    ```
    $ . ./set_environment_variables.sh
    ```

3. Download historical data from Coinbase and save it locally to disk
    ```
    $ make data
    ```

4. Train ML model
    ```
    $ make train
    ```

5. Deploy the model
    ```
    $ make deploy
    ```

6. Take the endpoint URL you get from Cerebrim in the previous step, and set the `CEREBRIUM_ENDPOINT_URL` variable in `set_environment_variables.sh`. Then re-run
    ```
    $ . ./set_environment_variables.sh
    ```

7. Test the endpoint works
    ```
    $ make test-endpoint
    ```
## Lectures

### 1. Model training

### 2. Model deployment as REST API

### 3. Automatic deployments from the Model Registry


## TODOs
- [x] Get data from Coinbase
- [x] Transform ts data into supervised ML data
- [x] Engineer a few features using technical indicators
- [x] Train a decent model with linear regression
- [x] Fix bug when computing tech indicators from raw prices
- [x] Deploy the modelLightGBMRegressor
- [x] Webhooks
    - [x] Add secrets to GitHub
    - [x] Trigger workflow from Comet ML model registry
- [ ] Optimize model hyper-parameter with out-of-time cross validation use 