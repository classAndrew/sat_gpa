from src.data import School
from src.util import get_GUID, get_school_names
from typing import List
import logging
import asyncio
import aiohttp

log = logging.getLogger("Cry About It")

class CryHTTPClient:
    """
    Async HTTP Client

    @type _session: aiohttp.Session
    @cvar _session: internal aiohttp session
    @cvar HEADERS: Proper headers, user-agent, etc.
    """

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9", 
        "Accept-Encoding": "gzip, deflate", 
        "DNT": "1", "Connection": 
        "close", "Upgrade-Insecure-Requests": "1",
        "sec-ch-ua": ' Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        "cookie":''
    }

    SCHOOL_URI = "https://www.niche.com/colleges/"
    SCHOOL_API = 'https://www.niche.com/api/scatterplot/plot/?guid=%s'
    LIST_URI = "https://www.niche.com/colleges/search/best-colleges/?page=%d"
    LIST_LIMIT = 112
    _session = aiohttp.ClientSession(headers=HEADERS)
    
    @staticmethod
    async def get_school(name: str) -> School: 
        """
        Gets school from the name
        @param name: string of school name
        @type name: str
        """
        
        res: aiohttp.ClientResponse = await CryHTTPClient._session.get(CryHTTPClient.SCHOOL_URI+name)
        if res.status != 200:
            raise Exception(f"{name}: {res.reason}")
        
        txt = await res.text()
        res.close()

        # get GUID
        try:
            guid = get_GUID(txt)
        except:
            log.error(f"GUID of {name} not found. Skipping")
            return None

        res: aiohttp.ClientResponse = await CryHTTPClient._session.get(CryHTTPClient.SCHOOL_API % guid)

        data_raw = await res.json()
        res.close()
        
        if not "plot" in data_raw:
            log.error(f"{name} no plot. Skipping")
            return None
            
        major_idx = data_raw["plot"]["attributes"].index("Major")
        major_conversion = data_raw["plot"]["attributeValues"][major_idx]+["Undecided"]
        SAT_idx = data_raw["plot"]["units"].index("SAT/ACT")
        GPA_idx = data_raw["plot"]["units"].index("GPA")
        decis_idx = data_raw["plot"]["attributes"].index("Decision")
        has_in_state = True
        try:
            state_idx = data_raw["plot"]["attributes"].index("In-State Status")
        except:
            log.warning(f"{name} does not have an in-state status")
            has_in_state = False

        records = []

        for pt in data_raw["plot"]["points"]:
            # skip it if it's a considering
            if not pt["attributes"][decis_idx]: continue
            # acc/rej, major, state, SAT, GPA
            major = pt["attributes"][major_idx] if pt["attributes"][major_idx] else -1
            SAT, GPA = pt["values"][SAT_idx], pt["values"][GPA_idx]

            if has_in_state:
                state = "out" if pt["attributes"][state_idx] else "in"
                records.append((int(pt["attributes"][decis_idx] == 1), major_conversion[major], 
                    state, int(round(SAT*1600, -1)), round(GPA*4, 2)))
            else:
                records.append((int(pt["attributes"][decis_idx] == 1), major_conversion[major], 
                    int(round(SAT*1600, -1)), round(GPA*4, 2)))
        school = School(name, guid, records)

        return school

    @staticmethod
    async def get_all_schools() -> List[str]:
        pages = [CryHTTPClient.LIST_URI % i for i in range(100, 113)]
        promises = await asyncio.gather(*map(CryHTTPClient._session.get, pages))
        txts = await asyncio.gather(*[x.text() for x in promises])
        school_names = [y for x in map(get_school_names, txts) for y in x]
        
        print('\n'.join(school_names))
        return school_names