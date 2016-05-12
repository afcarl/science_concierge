# Science Concierge: Rocchio algorithm and nearest neighbors

import os
import pandas as pd
import numpy as np
import scipy
from sklearn.neighbors import NearestNeighbors

__all__ = ["build_nearest_neighbors",
           "get_schedule_rocchio",
           "get_rocchio_topic"]

def build_nearest_neighbors(poster_vect, n_recommend=None):
    """
    Create nearest neighbors model using scikit-learn
    from svd matrix (also called poster vector)
    """
    if n_recommend is None:
        n_recommend = poster_vect.shape[0]
    nbrs_model = NearestNeighbors(n_neighbors=n_recommend).fit(poster_vect)
    return nbrs_model

def get_rocchio_topic(poster_vect, likes=(), dislikes=(),
                      w_like=1.8, w_dislike=0.2):
    """
    Give poster_vector matrix as numpy array
    and list of like and dislike posters,
    return topic preference using Rocchio algorithm

    Parameters
    ----------
    poster_vect: array of poster vectors where each row represents vector of
        each poster
    likes: list of like posters
    dislikes: list of dislike or non-relevant posters
    w_like: weight for like posters (so called alpha)
    w_dislike: weight for dislike posters (so called beta)
    """

    n, m = poster_vect.shape

    if scipy.sparse.issparse(poster_vect):
        a = 1
        b = 0.8
        c = -0.2
        W = [a]\
            + [b/len(likes)]*(len(likes)-1)\
            + [c/len(dislikes)]*(len(dislikes))
        sel_docs = likes + dislikes
        poster_vect_sel = [poster_vect[d] for d in sel_docs]
        topic_sel = scipy.sparse.vstack([w * t for (w, t) in zip(W, poster_vect_sel)])
        topic_pref = topic_sel.sum(axis=0) # in sparse case, use sum of vectors
    else:
        if len(likes) == 0:
            topic_like = np.zeros(m)
        else:
            topic_like = np.vstack(poster_vect[like] for like in likes)
            topic_like = topic_like.mean(0)

        if len(dislikes) == 0:
            topic_dislike = np.zeros(m)
        else:
            topic_dislike = np.vstack(poster_vect[dislike] for dislike in dislikes)
            topic_dislike = topic_dislike.mean(0)

        if len(likes) == 1 and len(dislikes) == 0:
            topic_pref = np.atleast_2d(topic_like) # equivalent to nearest neighbor
        else:
            topic_pref = np.atleast_2d(w_like*topic_like - w_dislike*topic_dislike)

    return topic_pref

def get_schedule_rocchio(nbrs_model, poster_vect, likes=(), dislikes=()):
    """
    Give list of like and dislike posters,
    return list of suggested posters (recommend_index)
    and nearest neighbor distance (recommend_distance)
    """
    topic_pref = get_rocchio_topic(poster_vect, like_posters, dislike_posters)
    recommend_distance, recommend_index = nbrs_model.kneighbors(topic_pref)
    return recommend_distance.flatten(), recommend_index.flatten()
