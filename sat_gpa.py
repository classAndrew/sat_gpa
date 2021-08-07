"""
Author: classAndrew 
Date: 3 Aug 2021
Description: Downloads data from Niche and shoves it in a binary classifier.
"""

from src.networking import CryHTTPClient
from src.util import HELP, config, Config
from src.classifier import SVM, Logistic, Tree
import logging
import asyncio
import sys
import os
import numpy as np

if __name__ == "__main__":
    log = logging.getLogger("Cry About It")
    hwdl = logging.StreamHandler()
    hwdl.setFormatter(logging.Formatter("[Cry]::[%(levelname)s] %(message)s"))
    log.addHandler(hwdl)
    log.setLevel(logging.DEBUG)

    log.info("CRY ABOUT IT: the college admissions prediction tool. Cry about not getting into your dream school :D")
    
    if "-h" in sys.argv or "--help" in sys.argv:
        print(HELP)
        exit(0)

    config = Config(sys.argv[1:])

    async def download(maxslice): 
        # if len(config.names) > 100:
        #     log.warning("aiohttp only allows a limit of 100 concurrent requests. Please make sure your college list is < 100")
        #     return

        offset = 0
        while offset < maxslice:
            res = await asyncio.gather(*map(CryHTTPClient.get_school, config.names[offset:offset+100]))

            if not config.out_dir:
                # dump it in stdout
                print(*zip(config.names, res.all_records))
                return
            
            if not os.path.exists(config.out_dir):
                os.mkdir(config.out_dir)

            for i in range(len(res)):
                name = config.names[i+offset]
                if not res[i]:
                    continue

                path = os.path.join(config.out_dir, name+".csv")

                s = '\n'.join(','.join(str(y) for y in x) for x in res[i].all_records)
                with open(path, 'w') as f:
                    f.write(s)
            
            offset += 100
            await asyncio.sleep(5)

    if config.do_rank:
        with open(config.file_list) as f:
            names = f.read().split('\n')
        
        ratings = []
        for i in range(len(names)):
            name = names[i]
            log.info(f"{i}-{name}")
            try:
                lr = Logistic(name)
                ratings.append((name, lr.score, lr.coef))
            except Exception as e:
                log.error(f"{i}-{name} does not have varying classes")
                continue            

        for name, score, coef in sorted(ratings, key=lambda x: x[1][0], reverse=True):
            coef = coef[0]
            if len(coef) == 3:
                coef = [coef[0], 0, *coef[1:]]
            print(f"{name}\nAccuracy: {score[0]:.3} ± {score[1]:.3}\n{np.round(coef, 4)}\n")
            
    elif config.is_predict:
        clf = Logistic(config.names[0])
        print(f"Accuracy: {clf.score[0]} ± {clf.score[1]}")
        print(clf.coef)

    else:
        asyncio.get_event_loop().run_until_complete(download(1000))
    # asyncio.get_event_loop().run_until_complete(CryHTTPClient.get_all_schools())
    asyncio.get_event_loop().run_until_complete(CryHTTPClient._session.close())
    