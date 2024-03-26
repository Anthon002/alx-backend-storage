#!/usr/bin/env python3
'''module with top_students function
'''


def top_students(mongo_collection):
    '''module that returns a list of students sorted by avg score
    '''
    stds = mongo_collection.aggregate(
        [
            {
                '$project': {
                    '_id': 1,
                    'name': 1,
                    'averageScore': {
                        '$avg': {
                            '$avg': '$topics.score',
                        },
                    },
                    'topics': 1,
                },
            },
            {
                '$sort': {'averageScore': -1},
            },
        ]
    )
    return stds
