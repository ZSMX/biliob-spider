from db import settings
from db import db
import datetime
import logging
from pymongo import DESCENDING


def computeVideoRank():
    coll = db['video']  # 获得collection的句柄

    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(levelname)s @ %(name)s: %(message)s')
    logger = logging.getLogger(__name__)

    logger.info("开始计算视频数据排名")

    i = 1

    keys = ['cView', 'cLike', 'cDanmaku', 'cFavorite', 'cCoin', 'cShare']
    for each_key in keys:
        logger.info("开始计算视频{}排名".format(each_key))
        i = 1
        videos = coll.find({each_key: {'$exists': 1}}, {'aid': 1, 'rank': 1, each_key: 1}).batch_size(
            300).sort(each_key, DESCENDING)
        if each_key == 'cView':
            each_rank = 'cViewRank'
            each_d_rank = 'dViewRank'

        each_rank = each_key + 'Rank'
        each_d_rank = 'd' + each_key[1:] + 'Rank'

        for each_video in videos:
            # 如果没有data 直接下一个
            if each_key in each_video:
                if 'rank' in each_video:
                    rank = each_video['rank']
                    if each_rank in each_video['rank']:
                        rank[each_d_rank] = each_video['rank'][each_rank] - i
                    else:
                        rank[each_d_rank] = -1
                    rank[each_rank] = i
                else:
                    rank = {
                        each_rank: i,
                        each_d_rank: -1
                    }
            if each_video[each_key] == 0:
                if 'rank' in each_video:
                    rank = each_video['rank']
                    rank[each_d_rank] = 0
                    rank[each_rank] = -1
                else:
                    rank = {
                        each_rank: -1,
                        each_d_rank: 0
                    }
            if each_key == keys[-1]:
                rank['updateTime'] = datetime.datetime.now()
            coll.update_one({'aid': each_video['aid']}, {
                '$set': {
                    'rank': rank,
                }
            })
            i += 1

        logger.info("完成计算视频数据排名")
