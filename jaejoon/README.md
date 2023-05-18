## model directory

-   contains trained model
-   baseline-1 : linear regression using image + title + metadata
    -   hyper parameters :
        -   learning rate : 1e-5
        -   batch size : 64
        -   epochs : 50
    -   best valid mse : 2.50 at epoch 50
    -   total training time : 82m 7s
    -   best_model test mse : 2.3506
-   baseline-2 : linear regression using title + metadata
    -   hyper parameters :
        -   learning rate : 1e-5
        -   batch size : 64
        -   epochs : 50
    -   best valid mse : 21.69 at epoch 50
    -   total training time : 79m 50s
    -   best_model test mse : 17.4423
-   baseline-3: linear regression using image + title + metadata
    -   hyper parameters :
        -   learning rate : 1e-5
        -   batch size : 64
        -   epochs : 50
    -   best valid mse : 2.45 at epoch 100
    -   total training time : 140m 3s
    -   best_model test mse : 2.3392
        -   no image test mse : 23.0688
        -   no title test mse : 2.3488
        -   no meta test mse : 2.6432

## baseline.ipynb

-   train simple linear regression model

## train_test_split.ipynb

-   split csv file that contains whole data to train, test data and save them as csv files

## train.ipynb

-   base code for training (baseline, our method)
