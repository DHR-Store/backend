 # app.py
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    import requests
    from bs4 import BeautifulSoup
    import base64
    import json
    import re

    app = Flask(__name__)
    CORS(app) # Enable CORS for all routes

    # Base URL for 4khdhub
    # IMPORTANT: This should be kept up-to-date if the actual 4khdhub domain changes.
    FOURKHDHUB_BASE_URL = "https://4khdhub.net"

    # --- Helper functions (mimicking the JS logic from your provided files) ---

    def rot13(s):
        """Applies ROT13 cipher to a string."""
        result = []
        for char in s:
            if 'a' <= char <= 'z':
                result.append(chr(((ord(char) - ord('a') + 13) % 26) + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(chr(((ord(char) - ord('A') + 13) % 26) + ord('A')))
            else:
                result.append(char)
        return "".join(result)

    def decode_string(encrypted_string):
        """Decodes a string using a sequence of base64 and ROT13 decodings."""
        try:
            decoded = base64.b64decode(encrypted_string).decode('utf-8')
            decoded = base64.b64decode(decoded).decode('utf-8')
            decoded = rot13(decoded)
            decoded = base64.b64decode(decoded).decode('utf-8')
            return json.loads(decoded)
        except Exception as e:
            print(f"Error decoding string: {e}")
            return None

    def encode_string(value):
        """Encodes a string using base64."""
        return base64.b64encode(value.encode('utf-8')).decode('utf-8')

    def pen_string(value):
        """Applies a custom ROT13-like encoding."""
        # This function is not directly used in the provided JS, but kept for completeness
        # if it were part of a more complex encoding scheme.
        return value.replace(/[a-zA-Z]/g, lambda char: chr(
            (90 if char.isupper() else 122) >= (ord(char) + 13)
            and (ord(char) + 13) or (ord(char) + 13 - 26)
        ))

    # The abortable_timeout function is for client-side JS.
    # It's not directly applicable to a synchronous Flask backend.
    # We will remove the `await abortable_timeout` calls in the Flask app
    # as they would block the server.

    async def get_redirect_links(link, headers):
        """Fetches redirect links from a given link."""
        try:
            res = requests.get(link, headers=headers)
            res.raise_for_status()
            res_text = res.text

            regex = r"ck\('_wp_http_\d+','([^']+)'"
            combined_string = "".join(re.findall(regex, res_text))
            
            # Replicating the decode(pen(decode(decode(combinedString)))) logic
            decoded_part1 = base64.b64decode(combined_string).decode('utf-8')
            decoded_part2 = base64.b64decode(decoded_part1).decode('utf-8')
            decoded_part3 = rot13(decoded_part2) # Assuming pen_string is rot13
            decoded_data_str = base64.b64decode(decoded_part3).decode('utf-8')
            
            data = json.loads(decoded_data_str)

            token = encode_string(data.get('data', ''))
            blog_link = data.get('wp_http1', '') + "?re=" + token

            # Removed blocking abortable_timeout here for backend
            # await abortable_timeout((data.get('total_time', 0) + 3) * 1000)

            vcloud_link = "Invalid Request"
            while "Invalid Request" in vcloud_link:
                blog_res = requests.get(blog_link, headers=headers)
                blog_res.raise_for_status()
                blog_res_text = blog_res.text
                if "Invalid Request" in blog_res_text:
                    print(blog_res_text)
                else:
                    match = re.search(r'var reurl = "([^"]+)"', blog_res_text)
                    if match:
                        vcloud_link = match.group(1)
                    else:
                        vcloud_link = blog_link # Fallback if regex fails
                    break
            return blog_link or link
        except Exception as err:
            print(f"Error in getRedirectLinks: {err}")
            return link

    # This is a placeholder for the actual hubcloudExtracter logic.
    # In a real scenario, you'd implement the scraping logic for hubcloud here.
    async def hubcloud_extracter(link):
        """Placeholder for hubcloud extractor."""
        print(f"Attempting to extract from hubcloud link: {link}")
        # Simulate fetching and parsing a video link
        # In a real scenario, this would involve more complex scraping
        # to find the actual video source URL.
        # For demonstration, we'll return a dummy video URL.
        return [{"url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4", "quality": "auto"}]


    # --- API Endpoints ---

    @app.route('/api/4khdhub/posts', methods=['GET'])
    async def get_4khdhub_posts():
        filter_param = request.args.get('filter', '')
        page = request.args.get('page', '1')
        search_query = request.args.get('searchQuery', '')

        url = ""
        if search_query:
            url = f"{FOURKHDHUB_BASE_URL}/page/{page}.html?s={search_query}"
        else:
            url = f"{FOURKHDHUB_BASE_URL}{filter_param}/page/{page}.html"

        print(f"Fetching 4khdhub posts from: {url}")
        try:
            response = requests.get(url)
            response.raise_for_status() # Raise an exception for HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')
            
            catalog = []
            for element in soup.select(".card-grid > *"):
                title_tag = element.select_one(".movie-card-title")
                link_tag = element.get('href')
                image_tag = element.select_one("img")

                title = title_tag.text.strip() if title_tag else None
                link = link_tag if link_tag else None
                image = image_tag.get('src') if image_tag else None

                if title and link and image:
                    catalog.append({"title": title, "link": link, "image": image})
            
            return jsonify(catalog)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching 4khdhub posts: {e}")
            return jsonify({"error": f"Failed to fetch posts from 4khdhub: {e}"}), 500
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return jsonify({"error": f"An unexpected error occurred: {e}"}), 500


    @app.route('/api/4khdhub/meta', methods=['GET'])
    async def get_4khdhub_meta():
        link = request.args.get('link', '')
        if not link:
            return jsonify({"error": "Link parameter is required"}), 400

        url = f"{FOURKHDHUB_BASE_URL}{link}"
        print(f"Fetching 4khdhub meta from: {url}")

        try:
            res = requests.get(url)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')

            media_type = "movie"
            if soup.select_one(".season-content"):
                media_type = "series"

            title = soup.select_one(".page-title").text.strip() if soup.select_one(".page-title") else ""
            image = soup.select_one(".poster-image img").get('src') if soup.select_one(".poster-image img") else ""
            synopsis = soup.select_one(".content-section p").text.strip() if soup.select_one(".content-section p") else ""
            imdb_id = "" # 4khdhub doesn't seem to provide IMDb ID directly

            links = []
            if media_type == "series":
                for season_item in soup.select(".season-item"):
                    season_title = season_item.select_one(".episode-title").text.strip()
                    direct_links = []
                    for episode_download_item in season_item.select(".episode-download-item"):
                        file_info = episode_download_item.select_one(".episode-file-info").text.strip().replace("\n", " ")
                        hubdrive_link = episode_download_item.select_one("a:contains('HubDrive')")
                        if hubdrive_link:
                            direct_links.append({"title": file_info, "link": hubdrive_link.get('href')})
                    if season_title and direct_links:
                        links.append({"title": season_title, "directLinks": direct_links})
            else: # movie
                for download_item in soup.select(".download-item"):
                    item_title = download_item.select_one(".flex-1.text-left.font-semibold").text.strip()
                    hubdrive_link = download_item.select_one("a:contains('HubDrive')")
                    if hubdrive_link:
                        links.append({"title": item_title, "directLinks": [{"title": item_title, "link": hubdrive_link.get('href')}]})
            
            return jsonify({
                "title": title,
                "synopsis": synopsis,
                "image": image,
                "imdbId": imdb_id,
                "type": media_type,
                "linkList": links
            })

        except requests.exceptions.RequestException as e:
            print(f"Error fetching 4khdhub meta: {e}")
            return jsonify({"error": f"Failed to fetch meta from 4khdhub: {e}"}), 500
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

    @app.route('/api/4khdhub/stream', methods=['GET'])
    async def get_4khdhub_stream():
        link = request.args.get('link', '')
        if not link:
            return jsonify({"error": "Link parameter is required"}), 400

        print(f"Fetching 4khdhub stream from: {link}")
        try:
            hubdrive_link = ""
            common_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': FOURKHDHUB_BASE_URL,
                'Connection': 'keep-alive',
            }

            if "hubdrive" in link:
                hubdrive_res = requests.get(link, headers=common_headers)
                hubdrive_res.raise_for_status()
                hubdrive_soup = BeautifulSoup(hubdrive_res.text, 'html.parser')
                hubdrive_link = hubdrive_soup.select_one(".btn.btn-primary.btn-user.btn-success1.m-1")
                hubdrive_link = hubdrive_link.get('href') if hubdrive_link else link
            else:
                res = requests.get(link, headers=common_headers)
                res.raise_for_status()
                text = res.text
                
                encrypted_string_match = re.search(r"s\('o','([^']+)'", text)
                if not encrypted_string_match:
                    return jsonify({"error": "Encrypted string not found"}), 500
                
                encrypted_string = encrypted_string_match.group(1)
                decoded_string = decode_string(encrypted_string)
                
                if not decoded_string or 'o' not in decoded_string:
                    return jsonify({"error": "Failed to decode encrypted string or missing 'o' key"}), 500

                link = base64.b64decode(decoded_string['o']).decode('utf-8')
                
                redirect_link = await get_redirect_links(link, common_headers)
                redirect_link_res = requests.get(redirect_link, headers=common_headers)
                redirect_link_res.raise_for_status()
                redirect_link_text = redirect_link_res.text
                
                # Attempt to find hubdrive link
                hubdrive_link_match = re.search(r'href="(https:\/\/hubcloud\.[^\/]+\/drive\/[^"]+)"', redirect_link_text)
                if hubdrive_link_match:
                    hubdrive_link = hubdrive_link_match.group(1)
                else:
                    # Fallback to cheerio-like selection if regex fails
                    soup_redirect = BeautifulSoup(redirect_link_text, 'html.parser')
                    h3_link = soup_redirect.select_one('h3:contains("1080p") a')
                    if h3_link:
                        hubdrive_link = h3_link.get('href')
                    else:
                        hubdrive_link = link # Fallback to original link if no specific hubdrive link found

                if "hubdrive" in hubdrive_link:
                    hubdrive_res = requests.get(hubdrive_link, headers=common_headers)
                    hubdrive_res.raise_for_status()
                    hubdrive_soup = BeautifulSoup(hubdrive_res.text, 'html.parser')
                    btn_link = hubdrive_soup.select_one(".btn.btn-primary.btn-user.btn-success1.m-1")
                    if btn_link:
                        hubdrive_link = btn_link.get('href')
            
            hubdrive_link_res = requests.get(hubdrive_link, headers=common_headers)
            hubdrive_link_res.raise_for_status()
            hubcloud_text = hubdrive_link_res.text
            
            hubcloud_link_match = re.search(r'<META HTTP-EQUIV="refresh" content="0; url=([^"]+)">', hubcloud_text, re.IGNORECASE)
            if hubcloud_link_match:
                hubcloud_link = hubcloud_link_match.group(1)
            else:
                hubcloud_link = hubdrive_link # Fallback

            # Call the placeholder hubcloudExtracter
            stream_data = await hubcloud_extracter(hubcloud_link)
            return jsonify(stream_data)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching 4khdhub stream: {e}")
            return jsonify({"error": f"Failed to fetch stream from 4khdhub: {e}"}), 500
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

    # Removed the if __name__ == '__main__': block for Vercel deployment.
    # Vercel's Python runtime automatically detects and runs the Flask app instance named 'app'.
    
