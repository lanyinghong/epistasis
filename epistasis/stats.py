__doc__ = """Submodule with useful statistics functions for epistasis model."""

# -----------------------------------------------------------------------
# Useful statistical metrics as methods
# -----------------------------------------------------------------------

import numpy as np
from scipy.stats import f, norm

# -----------------------------------------------------------------------
# Correlation metrics
# -----------------------------------------------------------------------

def pearson(y_obs, y_pred):
    """ Calculate pearson coefficient between two variables.
    """
    x = y_obs
    y = y_pred

    xbar = np.mean(y_obs)
    ybar = np.mean(y_pred)

    terms = np.zeros(len(x), dtype=float)

    for i in range(len(x)):
        terms[i] = (x[i] - xbar) * (y[i] - ybar)

    numerator = sum(terms)

    # calculate denominator
    xdenom = sum((x - xbar)**2)
    ydenom = sum((y - ybar)**2)
    denominator = np.sqrt(xdenom)*np.sqrt(ydenom)

    return numerator/denominator

def generalized_r2(y_obs, y_pred):
    """ Calculate the rquared between the observed and predicted y.
        See wikipedia definition of `coefficient of determination`.
    """
    # Mean fo the y observed
    y_obs_mean = np.mean(y_obs)
    # Total sum of the squares
    ss_total = sum((y_obs - y_obs_mean)**2)
    # Sum of squares of residuals
    ss_residuals = sum((y_obs - y_pred)**2)
    r_squared = 1 - (ss_residuals/ss_total)
    return r_squared

def explained_variance(y_obs, y_pred):
    """ Returns the explained variance
    """
    # Mean fo the y observed
    y_obs_mean = np.mean(y_obs)
    # Total sum of the squares
    ss_total = sum((y_obs - y_obs_mean)**2)
    # Explained sum of squares
    ss_regression = sum((y_pred - y_obs_mean)**2)
    r_squared = (ss_regression/ss_total)
    return r_squared

def ss_residuals(y_obs, y_pred):
    """ calculate residuals """
    return sum((y_obs - y_pred)**2)

def chi_squared(y_obs, y_pred):
    """ Calculate the chi squared between observed and predicted y. """
    return sum( (y_obs - y_pred)**2/ y_pred )

# -----------------------------------------------------------------------
# Model error statistics
# -----------------------------------------------------------------------

def false_positive_rate(y_obs, y_pred, upper_ci, lower_ci, sigmas=2):
    """ Calculate the false positive rate of predicted values. Finds all values that
        equal zero in the known array and calculates the number of false positives
        found in the predicted given the number of samples and sigmas.

        The defined bounds are:
            (number of sigmas) * errors / sqrt(number of samples)

        __Arguments__:

        `known` [array-like] : Known values for comparing false positives

        `predicted` [array-like] : Predicted values

        `errors` [array-like] : Standard error from model

        `n_samples` [int]: number of replicate samples

        `sigma` [int (default=2)] : How many standard errors away (2 == 0.05 false positive rate)

        __Returns__:

        `rate` [float] : False positive rate in data
    """

    N = len(y_obs)
    # Check that known, predicted, and errors are the same size.
    if N != len(y_pred) or N != len(upper_ci):
        raise Exception("Input arrays must all be the same size")

    # Number of known-zeros:
    known_zeros = 0

    # Number of false positives:
    false_positives = 0

    # Scale confidence bounds to the number of samples and sigmas
    upper_bounds = sigmas * upper_ci
    lower_bounds = sigmas * lower_ci

    for i in range(N):
        # Check that known value is zero
        if y_obs[i] == 0.0:

            # Add count to known_zero
            known_zeros += 1

            # Calculate bounds with given number of sigmas.
            upper = y_pred[i] + upper_bounds[i]
            lower = y_pred[i] - lower_bounds[i]

            # Check false positive rate.
            if y_obs[i] > upper or y_obs[i] < lower:
                false_positives += 1

    # Calculate false positive rate
    rate = false_positives/float(known_zeros)

    return rate
    
    
def false_negative_rate(y_obs, y_pred, upper_ci, lower_ci, sigmas=2):
    """ Calculate the false negative rate of predicted values. Finds all values that
        equal zero in the known array and calculates the number of false negatives
        found in the predicted given the number of samples and sigmas.

        The defined bounds are:
            (number of sigmas) * errors / sqrt(number of samples)

        __Arguments__:

        `known` [array-like] : Known values for comparing false negatives

        `predicted` [array-like] : Predicted values

        `errors` [array-like] : Standard error from model

        `n_samples` [int]: number of replicate samples

        `sigma` [int (default=2)] : How many standard errors away (2 == 0.05 false negative rate)

        __Returns__:

        `rate` [float] : False negative rate in data
    """

    N = len(y_obs)
    # Check that known, predicted, and errors are the same size.
    if N != len(y_pred) or N != len(upper_ci):
        raise Exception("Input arrays must all be the same size")

    # Number of known-zeros:
    known_nonzeros = 0

    # Number of false negatives:
    false_negatives = 0

    # Scale confidence bounds to the number of samples and sigmas
    upper_bounds = sigmas * upper_ci
    lower_bounds = sigmas * lower_ci

    for i in range(N):
        # Check that known value is zero
        if y_obs[i] != 0.0:

            # Add count to known_zero
            known_nonzeros += 1

            # Calculate bounds with given number of sigmas.
            upper = y_pred[i] + upper_bounds[i]
            lower = y_pred[i] - lower_bounds[i]
            
            # Check false negative rate.
            if lower < 0 < upper:
                false_negatives += 1

    # Calculate false positive rate
    rate = false_negatives/float(known_nonzeros)

    return rate
    
    
# -----------------------------------------------------------------------
# Methods for model comparison
# -----------------------------------------------------------------------

def log_likelihood(model):
    """ Calculate the maximum likelihood estimate from sum of squared residuals."""


    N = model.n
    sigma = float(ssr/ N)
    L = N * np.log(1.0 / np.sqrt(2*np.pi*sigma)) - (1.0 / (2.0*sigma)) * ssr
    return L

def AIC(model):
    """ Calculate the Akaike information criterion score for a model. """
    k = len(model.Interactions.values)
    aic = 2 * k - 2 * log_likelihood(model)
    return aic

def log_likelihood_ratio(model1, model2):
    """ Calculate the likelihood ratio two regressed epistasis models.

        Models must be instances of ProjectedEpistasisModel
    """
    ssr1 = ss_residuals(model1.phenotypes, model1.predict())
    ssr2 = ss_residuals(model2.phenotypes, model2.predict())

    sigma1 = float(ssr1/model1.n)
    sigma2 = float(ssr2/model2.n)

    L1 = (1.0/ np.sqrt(2*np.pi*s1)) ** model1.n * np.exp(-ssr1/(sigma1*2.0))
    L2 = (1.0/ np.sqrt(2*np.pi*s2)) ** model2.n * np.exp(-ssr2/(sigma2*2.0))

    AIC1 = 2*df1 - 2*L1
    AIC2 = 2*df2 - 2*L2

    ratio = np.exp(AIC1-AIC2/2)
    return ratio

def F_test(model1, model2):
    """ Compare two models. """
    # Check that model1 is nested in model2. Not an intelligent test of this, though.
    if len(model1.Interactions.values) >= len(model2.Interactions.values):
        raise Exception("model1 must be nested in model2.")

    # number of observations
    n_obs = len(model1.phenotypes)

    # Number of parameters in each model
    p1 = len(model1.Interactions.values)
    p2 = len(model2.Interactions.values)
    df1 = p2-p1
    df2 = n_obs - p2 - 1

    # Sum of square residuals for each model.
    sse1 = ss_residuals(model1.phenotypes, model1.predict())
    sse2 = ss_residuals(model2.phenotypes, model2.predict())

    # F-score
    F = ( (sse1 - sse2) / df1 ) / (sse2 / df2)

    # get p-value from F-distribution
    p_value = 1 - f.cdf(F, df1, df2)
    return F, p_value
