# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import asyncio
from prisma import Prisma
from pysel.items import ProductItem


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class PyselPipeline:
   async def process_item(self, item, spider):
        if isinstance(item, ProductItem):
            db = Prisma()
            await db.connect()
            post = await db.post.create(
        {
            'name': item['name'],
            'price': item['price'],
        }
    )
        await db.disconnect()
        return item