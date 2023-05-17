## model directory :

-   contains model checkpoints
-   baseline-1 : linear regression using image + title + metadata
    -   best valid mse : 2.50 at epoch 50
    -   total training time : 82m 7s
    -   best_model test mse : 2.3506
-   baseline-2 : linear regression using title + metadata
    -   best valid mse : 21.69 at epoch 50
    -   total training time : 79m 50s
    -   best_model test mse : 17.4423

## baseline.ipynb

-   train simple linear regression model

## train_test_split.ipynb

-   split csv file that contains whole data to train, test data and save them as csv files

## train.ipynb

-   base code for train models (baseline, our method)
