#!/usr/bin/env python
# coding: utf-8

# In[6]:


import json
import logging


from microkit.utils import collect_cet_now

# In[7]:


logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
)
LOGGER = logging.getLogger(__name__)


# In[8]:


def handler(event, context):
    """Handler function for the API gateway"""
    timestamp = collect_cet_now()
    status_code = 200
    resp = {"statusCode": status_code, "data": {"cet_now": timestamp}}
    LOGGER.info("Lambda executed successfully!")
    return {"statusCode": 200, "body": json.dumps(resp)}

