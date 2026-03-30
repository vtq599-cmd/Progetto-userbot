import aiohttp
import io
import random
from telethon import events

async def _search(query):
    payload = {
        "query": """
        query SubredditQuery($url: String!, $filter: SubredditPostFilter, $iterator: String) {
            getSubreddit(url: $url) {
                children(limit: 30, iterator: $iterator, filter: $filter, disabledHosts: null) {
                    iterator
                    items {
                        ... on SubredditPost {
                            title
                            mediaSources { url }
                        }
                    }
                }
            }
        }
        """,
        "variables": {"url": f"/r/{query}", "filter": None, "iterator": None},
    }
    async with aiohttp.ClientSession() as s:
        async with s.post(
            "https://api.scrolller.com/api/v2/graphql",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=20),
        ) as r:
            data = await r.json()
    items = data.get("data", {}).get("getSubreddit", {}).get("children", {}).get("items", [])
    return [item["mediaSources"][0]["url"] for item in items if item.get("mediaSources")]

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}gallery ?(.*)", outgoing=True))
    async def gallery_handler(event):
        query = event.pattern_match.group(1).strip()
        if not query:
            await event.edit("❌ Укажи категорию\nПример: `.gallery cats`")
            return
        await event.edit("🖼 **Ищу изображения...**")
        try:
            urls = await _search(query)
            if not urls:
                return await event.edit(f"❌ Ничего не найдено по запросу: `{query}`")
            img_url = random.choice(urls)
            async with aiohttp.ClientSession() as s:
                async with s.get(img_url, timeout=aiohttp.ClientTimeout(total=30)) as r:
                    img_bytes = await r.read()
            file = io.BytesIO(img_bytes)
            file.name = f"scrolller.{img_url.split('.')[-1].split('?')[0]}"
            await event.delete()
            await client.send_file(event.chat_id, file, caption=f"🖼 **r/{query}**")
        except Exception as e:
            await event.edit(f"❌ {e}")

    @client.on(events.NewMessage(pattern=rf"\{prefix}gallerycat ?(.*)", outgoing=True))
    async def gallerycat_handler(event):
        query = event.pattern_match.group(1).strip()
        if not query:
            await event.edit("❌ Укажи категорию\nПример: `.gallerycat cats`")
            return
        await event.edit("🖼 **Ищу изображения...**")
        try:
            urls = await _search(query)
            if not urls:
                return await event.edit(f"❌ Ничего не найдено по запросу: `{query}`")
            chosen = random.sample(urls, min(4, len(urls)))
            files = []
            async with aiohttp.ClientSession() as s:
                for url in chosen:
                    async with s.get(url, timeout=aiohttp.ClientTimeout(total=30)) as r:
                        img_bytes = await r.read()
                    buf = io.BytesIO(img_bytes)
                    buf.name = f"scrolller.{url.split('.')[-1].split('?')[0]}"
                    files.append(buf)
            await event.delete()
            await client.send_file(event.chat_id, files, caption=f"🖼 **r/{query}**")
        except Exception as e:
            await event.edit(f"❌ {e}")
