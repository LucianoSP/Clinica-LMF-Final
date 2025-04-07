
@app.get("/test-google")
async def test_google():
    """Testa o acesso ao Google"""
    automation = None
    try:
        automation = UnimedAutomation()
        automation.setup_driver()

        result = automation.test_google()
        return result

    except Exception as e:
        logger.error(f"Erro no teste do Google: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if automation:
            automation.close()


@app.get("/test-urls")
async def test_unimed_urls():
    """Testa acesso a diferentes URLs da Unimed"""
    automation = None
    try:
        automation = UnimedAutomation()
        automation.setup_driver()

        results = automation.test_urls()
        return {
            "status": "completed",
            "results": results
        }

    except Exception as e:
        logger.error(f"Erro no teste de URLs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if automation:
            automation.close()


@app.get("/check-cloudflare")
async def check_cloudflare():
    """Verifica se os sites estão usando Cloudflare"""
    import requests
    import socket

    urls = [
        "https://www.uol.com.br",
        "https://www.google.com",
        "https://www.unimed.coop.br/site/",
        "https://www.unimedgoiania.coop.br",
        "https://sgucard.unimedgoiania.coop.br"
    ]

    results = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/132.0.0.0 Safari/537.36'
    }

    for url in urls:
        try:
            print(f"\nVerificando: {url}")
            # Resolve IP
            domain = url.split("//")[1].split("/")[0]
            ip = socket.gethostbyname(domain)

            # Faz requisição
            response = requests.get(url, headers=headers, timeout=10)

            # Verifica headers do Cloudflare
            cloudflare_headers = {
                'cf-ray': response.headers.get('cf-ray'),
                'cf-cache-status': response.headers.get('cf-cache-status'),
                'server': response.headers.get('server')
            }

            result = {
                "url": url,
                "ip": ip,
                "status_code": response.status_code,
                "is_cloudflare": any([
                    'cloudflare' in str(response.headers.get('server', '')).lower(),
                    'cf-ray' in response.headers,
                    ip.startswith(('104.16.', '172.64.', '104.18.'))
                ]),
                "cloudflare_headers": cloudflare_headers
            }

            print(f"Status: {response.status_code}")
            print(f"IP: {ip}")
            print(f"Cloudflare headers: {cloudflare_headers}")

        except Exception as e:
            print(f"Erro ao verificar {url}: {str(e)}")
            result = {
                "url": url,
                "error": str(e)
            }

        results.append(result)

    return {
        "status": "completed",
        "results": results
    }

@app.get("/test-simple")
async def test_simple_request():