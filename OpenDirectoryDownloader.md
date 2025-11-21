# How to Use OpenDirectoryDownloader.exe

Command line parameters:

Short	Long	Description
-u	--url	Url to scan
-t	--threads	Number of threads (default 5)
-o	--timeout	Number of seconds for timeout
-w	--wait	Number of seconds to wait between calls (when single threaded is too fast..)
-q	--quit	Quit after scanning (No "Press a key")
-c	--clipboard	Automatically copy the Reddits stats once the scan is done
-j	--json	Save JSON file
-f	--no-urls	Do not save URLs file
-f	--aria2-urls	Save aria2 urls files (with directory support)
-r	--no-reddit	Do not show Reddit stats markdown
-l	--upload-urls	Uploads urls file
-e	--exact-file-sizes	Exact file sizes (WARNING: Uses HEAD requests which takes more time and is heavier for server)
--fast-scan	Only use sizes from HTML, no HEAD requests, even if the approx. size cannot be extracted from the HTML
-s	--speedtest	Does a speed test after indexing
-a	--user-agent	Use custom default User Agent
--username	Username
--password	Password
--github-token	GitHub Token
-H	--header	Supply a custom header to use for each HTTP request. Can be used multiple times for multiple headers. See below for more info.
--output-file	Output file to use for urls file
--proxy-address	Proxy address, like "socks5://127.0.0.1:9050" (needed for .onion)
--proxy-username	Proxy username
--proxy-password	Proxy password
--no-browser	Disallow starting Chromium browser (for Cloudflare)

#Example

OpenDirectoryDownloader.exe --url "https://myopendirectory.com"

