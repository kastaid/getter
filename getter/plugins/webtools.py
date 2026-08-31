# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
import ipaddress
from time import monotonic
from urllib.parse import urlparse

from . import (
    Fetch,
    format_bytes,
    formatx_send,
    humanbool,
    import_lib,
    is_url,
    kasta_cmd,
    parse_pre,
    plugins_help,
)

_DNS_RECORD_TYPES = {
    1: "A",
    2: "NS",
    5: "CNAME",
    6: "SOA",
    15: "MX",
    16: "TXT",
    28: "AAAA",
    257: "CAA",
}


@kasta_cmd(
    pattern="(google|bing|yahoo|duck|yandex|startpage|brave|baidu)(?: |$)(.*)",
)
async def _(kst):
    engine = kst.pattern_match.group(1)
    keywords = await kst.client.get_text(kst, group=2)
    if not keywords:
        return await kst.eor("`Provide a keywords!`", time=5)
    yy = await kst.eor("`Searching...`")
    if engine == "google":
        search = "Google"
        url = "https://www.google.com/search?q={}"
    elif engine == "bing":
        search = "Bing"
        url = "https://www.bing.com/search?q={}"
    elif engine == "yahoo":
        search = "Yahoo"
        url = "https://search.yahoo.com/search?p={}"
    elif engine == "duck":
        search = "DuckDuckGo"
        url = "https://duckduckgo.com/?q={}"
    elif engine == "yandex":
        search = "Yandex"
        url = "https://yandex.com/search/?text={}"
    elif engine == "startpage":
        search = "Startpage"
        url = "https://www.startpage.com/sp/search?query={}"
    elif engine == "brave":
        search = "Brave"
        url = "https://search.brave.com/search?q={}"
    elif engine == "baidu":
        search = "Baidu"
        url = "https://www.baidu.com/s?wd={}"
    result = url.format(keywords.replace("\n", " ").replace(" ", "+")).strip()
    keywords = keywords.replace("\n", " ").strip()
    await yy.eor(f"**🔎 {search} Search Result**:\n\n[{keywords}]({result})")


@kasta_cmd(
    pattern="(un|)short(?: |$)(.*)",
)
async def _(kst):
    text = await kst.client.get_text(kst, group=2)
    if not text or not is_url(text):
        return await kst.eor("`Provide a valid link!`", time=5)
    yy = await kst.eor("`Processing...`")
    if kst.pattern_match.group(1).strip() == "un":
        res = await Fetch(
            text,
            real=True,
            allow_redirects=False,
            statuses=set(range(301, 308)),
        )
        if not res:
            return await yy.eod("`Try again now!`")
        output = "• **Unshorted Link**: {}\n• **Original Link**: {}".format(res.headers.get("location"), text)
    else:
        url = f"https://da.gd/s?url={text}"
        res = await Fetch(url)
        if not res:
            return await yy.eod("`Try again now!`")
        output = f"• **Shorted Link**: {res.strip()}\n• **Original Link**: {text}"
    await yy.eor(output)


@kasta_cmd(
    pattern="ip$",
)
async def _(kst):
    yy = await kst.eor("`Processing...`")
    ip = await myip()
    await yy.eor(ip, parse_mode=parse_pre)


@kasta_cmd(
    pattern="ipinfos?(?: |$)(.*)",
)
async def _(kst):
    ipaddr = await kst.client.get_text(kst)
    if not ipaddr or not is_ipv4(ipaddr):
        return await kst.eor("`Provide a valid IP address!`", time=5)
    yy = await kst.eor("`Processing...`")
    url = f"http://ip-api.com/json/{ipaddr}?fields=status,message,continent,country,countryCode,regionName,city,zip,lat,lon,timezone,currency,isp,mobile,query"
    res = await Fetch(url, re_json=True)
    if not res:
        return await yy.eod("`Try again now!`")
    if str(res.get("status")).lower() == "success":
        coordinates = str(res.get("lat") or "") + "," + str(res.get("lon") or "")
        text = """<b><u>IP Address Information</u></b>
├  <b>IP</b>: <code>{}</code>
├  <b>City</b>: <code>{}</code>
├  <b>Region</b>: <code>{}</code>
├  <b>Country</b>: <code>{}</code>
├  <b>Country Code</b>: <code>{}</code>
├  <b>Currency</b>: <code>{}</code>
├  <b>Continent</b>: <code>{}</code>
├  <b>Coordinates</b>: <code>{}</code>
├  <b>Time Zone</b>: <code>{}</code>
├  <b>ISP</b>: <code>{}</code>
├  <b>Mobile</b>: <code>{}</code>
└  <b>Map</b>: <code>{}</code>""".format(
            res.get("query"),
            res.get("city") or "?",
            res.get("regionName") or "?",
            res.get("country") or "?",
            res.get("countryCode") or "?",
            res.get("currency") or "?",
            res.get("continent") or "?",
            coordinates,
            res.get("timezone") or "?",
            res.get("isp") or "?",
            humanbool(res.get("mobile")),
            f"https://www.google.com/maps?q={coordinates}",
        )
    else:
        text = """<b><u>IP Address Information</u></b>
├  <b>IP</b>: <code>{}</code>
├  <b>Status</b>: <code>{}</code>
└  <b>Message</b>: <code>{}</code>""".format(
            res.get("query"),
            res.get("status"),
            res.get("message"),
        )
    await yy.eor(text, parse_mode="html")


@kasta_cmd(
    pattern="speedtest$",
)
async def _(kst):
    start = monotonic()
    yy = await kst.eor("`Processing...`")
    try:
        import speedtest
    except ImportError:
        speedtest = import_lib(
            lib_name="speedtest",
            pkg_name="speedtest-cli==2.1.3",
        )
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        st.download()
        st.upload()
        resp = st.results.dict()
        client = resp.get("client")
        text = """<b><u>SpeedTest completed in {:.3f}s</u></b>
├  <b>Download</b>: <code>{}</code>
├  <b>Upload</b>: <code>{}</code>
├  <b>Ping</b>: <code>{}</code>
├  <b>Internet Service Provider</b>: <code>{}</code>
┊  ├  <b>Rating</b>: <code>{}</code>
┊  ├  <b>IP</b>: <code>{}</code>
┊  ├  <b>Country</b>: <code>{}</code>
└  <b>Sponsor</b>: <code>{}</code>""".format(
            monotonic() - start,
            format_bytes(resp.get("download")),
            format_bytes(resp.get("upload")),
            resp.get("ping"),
            client.get("isp"),
            client.get("isprating"),
            client.get("ip"),
            client.get("country"),
            resp.get("server").get("sponsor"),
        )
        await yy.eor(text, parse_mode="html")
    except Exception as err:
        await yy.eor(formatx_send(err), parse_mode="html")


@kasta_cmd(
    pattern="pinger(?: |$)(.*)",
)
async def _(kst):
    dns = await kst.client.get_text(kst)
    if not dns:
        return await kst.eor("`Provide a valid DNS or IP address!`", time=5)
    yy = await kst.eor("`Processing...`")
    duration = await pinger(dns)
    await yy.eor(f"• **DNS**: `{dns}`\n• **Ping Speed**: `{duration}`")


@kasta_cmd(
    pattern="http(?: |$)(.*)",
)
async def _(kst):
    link = await kst.client.get_text(kst)
    if not link:
        return await kst.eor("`Provide a valid URL!`", time=5)
    if not is_url(link):
        return await kst.eod("`URL must start with http:// or https://`")
    yy = await kst.eor("`Processing...`")
    res = await Fetch(link, head=True, real=True)
    if res:
        headers = "\n".join(f"{k}: {v}" for k, v in res.headers.items())
        res.close()
        return await yy.eor(
            f"<b>HTTP Headers {link}</b>\n<pre>{headers}</pre>",
            parts=True,
            parse_mode="html",
        )
    await yy.eod(f"`Cannot fetch HTTP headers for {link}.`")


@kasta_cmd(
    pattern="dns(?: |$)(.*)",
)
async def _(kst):
    link = await kst.client.get_text(kst)
    if not link:
        return await kst.eor("`Provide a valid URL!`", time=5)
    if not is_url(link):
        return await kst.eod("`URL must start with http:// or https://`")
    yy = await kst.eor("`Processing...`")
    hostname = urlparse(link).hostname
    if not hostname:
        return await yy.eod("`Cannot extract hostname from URL.`")

    async def resolve(record_type: str):
        return await Fetch(
            "https://cloudflare-dns.com/dns-query",
            headers={"Accept": "application/dns-json"},
            params={"name": hostname, "type": record_type},
            re_json=True,
        )

    results = await asyncio.gather(*(resolve(i) for i in _DNS_RECORD_TYPES.values()), return_exceptions=True)
    records = format_dns_records(results)
    if records:
        return await yy.eor(
            f"<b>DNS Records {hostname}</b>\n{records}",
            parts=True,
            parse_mode="html",
        )
    await yy.eod(f"`No DNS records found for {hostname}.`")


@kasta_cmd(
    pattern="whois(?: |$)(.*)",
)
async def _(kst):
    link = await kst.client.get_text(kst)
    if not link:
        return await kst.eor("`Provide a valid URL or IP address!`", time=5)
    if not is_url(link) and not is_ipv4(link):
        return await kst.eod("`URL must start with http:// or https://, or provide a valid IP address.`")
    yy = await kst.eor("`Processing...`")
    target = link if is_ipv4(link) else urlparse(link).hostname
    if not target:
        return await yy.eod("`Invalid URL or IP address!`")
    res = await rdap(target)
    if res:
        return await yy.eor(
            f"<b>WHOIS For {target}</b>\n{res}",
            parts=True,
            parse_mode="html",
        )
    await yy.eod(f"`Cannot resolve WHOIS information for {target}.`")


async def rdap(target: str) -> str | None:
    try:
        ip = ipaddress.ip_address(target)
    except ValueError:
        ip = None
    if ip:
        bootstrap = f"https://data.iana.org/rdap/ipv{ip.version}.json"
        key = "ip"
    else:
        bootstrap = "https://data.iana.org/rdap/dns.json"
        key = "domain"
    data = await Fetch(bootstrap, re_json=True)
    if not data:
        return
    if ip:
        base = next(
            (
                service[1][0]
                for service in data.get("services", [])
                if any(ip in ipaddress.ip_network(cidr) for cidr in service[0])
            ),
            None,
        )
    else:
        tld = target.rsplit(".", 1)[-1].lower()
        base = next(
            (service[1][0] for service in data.get("services", []) if tld in service[0]),
            None,
        )
    if not base:
        return
    res = await Fetch(
        f"{base.rstrip('/')}/{key}/{target}",
        re_json=True,
    )
    if not res:
        return

    def entities(value: dict) -> list[dict]:
        result = []
        for entity in value.get("entities", []):
            result.append(entity)
            result.extend(entities(entity))
        return result

    def vcard_value(entity: dict, field: str) -> str | None:
        vcard = entity.get("vcardArray")
        if not isinstance(vcard, list) or len(vcard) < 2:
            return
        for item in vcard[1]:
            if not isinstance(item, list) or len(item) < 4:
                continue
            if item[0] != field:
                continue
            value = item[3]
            if isinstance(value, list):
                value = ", ".join(str(i) for i in value if i)
            elif item[2] == "uri":
                value = str(value)
            if value:
                return value

    def entity_value(
        roles: tuple[str, ...],
        field: str,
    ) -> str:
        for entity in entities(res):
            if set(roles) & set(entity.get("roles", [])):
                value = vcard_value(entity, field)
                if value:
                    return value
        return "?"

    def entity_port43(roles: tuple[str, ...]) -> str:
        for entity in entities(res):
            if set(roles) & set(entity.get("roles", [])):
                value = entity.get("port43")
                if value:
                    return str(value)
        return "?"

    def event_date(action: str) -> str:
        for event in res.get("events", []):
            if event.get("eventAction") == action:
                value = event.get("eventDate")
                if value:
                    return str(value).split("T")[0]
        return "?"

    def add(label: str, value: object, code: bool = False) -> None:
        if value is None:
            return
        value = str(value).strip()
        if not value or value == "?":
            return
        if code:
            value = f"<code>{value}</code>"
        lines.append(f"<b>{label}</b>: {value}")

    lines = []
    if ip:
        cidrs = res.get("cidr0_cidrs", [])
        network = "?"
        if cidrs:
            cidr = cidrs[0]
            prefix = cidr.get(f"v{ip.version}prefix")
            length = cidr.get("length")
            if prefix is not None and length is not None:
                network = f"{prefix}/{length}"
        add("IP", target, True)
        add("Network", network, True)
        start = res.get("startAddress")
        end = res.get("endAddress")
        if start and end:
            add("Range", f"{start} - {end}", True)
        add("Name", res.get("name"), True)
        add("Country", res.get("country"), True)
        add(
            "Organization",
            entity_value(
                ("registrant", "administrative", "technical"),
                "org",
            ),
        )
        add("Type", res.get("type"), True)
        add("Status", ", ".join(res.get("status", [])))
        add(
            "Email",
            entity_value(
                ("registrant", "administrative", "technical"),
                "email",
            ),
            True,
        )
        add(
            "Phone",
            entity_value(
                ("registrant", "administrative", "technical"),
                "tel",
            ),
            True,
        )
        add(
            "Address",
            entity_value(
                ("registrant", "administrative", "technical"),
                "adr",
            ),
            True,
        )
        add("Abuse Email", entity_value(("abuse",), "email"), True)
        add(
            "WHOIS Server",
            entity_port43(("registrant", "administrative", "technical", "abuse")),
            True,
        )
    else:
        registrar = entity_value(("registrar",), "fn")
        registrar_id = "?"
        for entity in entities(res):
            if "registrar" not in entity.get("roles", []):
                continue
            for public_id in entity.get("publicIds", []):
                if public_id.get("identifier"):
                    registrar_id = str(public_id["identifier"])
                    break
            if registrar_id != "?":
                break
        add(
            "Domain",
            res.get("ldhName") or res.get("unicodeName") or target,
            True,
        )
        add("ID", res.get("handle"), True)
        add("Registrar", registrar)
        add("Registrar ID", registrar_id, True)
        add("Created", event_date("registration"), True)
        add("Updated", event_date("last changed"), True)
        add("Expires", event_date("expiration"), True)
        add("Status", ", ".join(res.get("status", [])))
        add(
            "Email",
            entity_value(
                ("registrant", "administrative", "technical"),
                "email",
            ),
            True,
        )
        add(
            "Phone",
            entity_value(
                ("registrant", "administrative", "technical"),
                "tel",
            ),
            True,
        )
        add(
            "Address",
            entity_value(
                ("registrant", "administrative", "technical"),
                "adr",
            ),
            True,
        )
        add("Abuse Email", entity_value(("abuse",), "email"), True)
        add(
            "WHOIS Server",
            entity_port43(
                (
                    "registrant",
                    "administrative",
                    "technical",
                    "registrar",
                    "abuse",
                )
            ),
            True,
        )
        nameservers = [
            ns.get("ldhName") or ns.get("unicodeName")
            for ns in res.get("nameservers", [])
            if ns.get("ldhName") or ns.get("unicodeName")
        ]
        if nameservers:
            lines.append("<b>Nameservers</b>:")
            lines.extend(f"• <code>{ns}</code>" for ns in nameservers)

        dnssec = res.get("secureDNS", {}).get("delegationSigned")
        if dnssec is not None:
            add("DNSSEC", "Yes" if dnssec else "No")
    return "\n".join(lines)


async def pinger(addr: str) -> str:
    try:
        import icmplib
    except ImportError:
        icmplib = import_lib(
            lib_name="icmplib",
            pkg_name="icmplib==3.0.4",
        )
    try:
        res = await icmplib.async_ping(
            addr,
            count=1,
            interval=0.1,
            timeout=2,
            privileged=False,
        )
        if res.is_alive:
            return f"{res.avg_rtt}ms"
    except BaseException:
        pass
    try:
        proc = await asyncio.create_subprocess_exec(
            "ping",
            "-c",
            "1",
            addr,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        out, _ = await proc.communicate()
        if proc.returncode == 0:
            for i in out.decode().splitlines():
                if "min/avg/max" in i:
                    rtt = i.replace(" ", "").split("=")[-1].split("/")[1]
                    return f"{rtt}ms"
    except BaseException:
        pass
    return "--ms"


async def myip() -> str:
    ips = (
        "https://checkip.amazonaws.com",
        "https://ipinfo.io/ip",
        "https://4.ident.me",
    )
    for url in ips:
        res = await Fetch(url, re_content=True)
        if res:
            return res.decode("utf-8").strip()
        continue
    return "null"


def format_dns_records(results: list) -> str:
    records = []
    seen = set()
    for res in results:
        if not isinstance(res, dict):
            continue
        for record in res.get("Answer", []):
            record_type = record.get("type")
            value = record.get("data")
            if not record_type or not value:
                continue
            name = _DNS_RECORD_TYPES.get(record_type, str(record_type))
            item = (name, value)
            if item in seen:
                continue
            seen.add(item)
            records.append(f"<b>{name}</b>: <code>{value}</code>")
    return "\n".join(records)


def is_ipv4(value: str) -> bool:
    try:
        ipaddress.IPv4Address(value)
        return True
    except (
        ValueError,
        TypeError,
    ):
        return False


plugins_help["webtools"] = {
    "{pfx}google [keywords]/[reply]": "Search with Google.",
    "{pfx}bing [keywords]/[reply]": "Search with Bing.",
    "{pfx}yahoo [keywords]/[reply]": "Search with Yahoo.",
    "{pfx}duck [keywords]/[reply]": "Search with DuckDuckGo.",
    "{pfx}yandex [keywords]/[reply]": "Search with Yandex.",
    "{pfx}startpage [keywords]/[reply]": "Search with Startpage.",
    "{pfx}brave [keywords]/[reply]": "Search with Brave.",
    "{pfx}baidu [keywords]/[reply]": "Search with Baidu.",
    "{pfx}short [link]/[reply]": "Shorten a link.",
    "{pfx}unshort [short_link]/[reply]": "Get the original link.",
    "{pfx}ip": "Get my current public IP address.",
    "{pfx}ipinfo [ip_address]/[reply]": "Get information about an IP address.",
    "{pfx}speedtest": "Test my server speed with Ookla.",
    "{pfx}pinger [dns/ip]/[reply]": "Ping a DNS or IP address.",
    "{pfx}http [url]/[reply]": "Show HTTP headers for a URL.",
    "{pfx}dns [url]/[reply]": "Get DNS records for a URL.",
    "{pfx}whois [url/ip]/[reply]": "Get WHOIS information for a URL or IP address.",
}
