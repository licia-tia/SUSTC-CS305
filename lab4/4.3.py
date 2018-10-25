# -*- coding: utf-8 -*-

import asyncio
import os
import mimetypes
import posixpath


def guess_type(path):
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream',  # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain'
    })
    base, ext = posixpath.splitext(path)
    if ext in extensions_map:
        return extensions_map[ext]
    ext = ext.lower()
    if ext in extensions_map:
        return extensions_map[ext]
    else:
        return extensions_map['']


async def dispatch(reader, writer):
    flag = False
    message = []
    while True:
        data = await reader.readline()
        message = message + data.decode().split(' ')
        if data == b'\r\n':
            break
    path = "." + message[1]
    print(message)
    print(path)
    if message[0] == "GET":
        if 'Cookie:' in message:
            if (message[message.index('Cookie:') + 1].replace("\r\n", "") != "./") & (path == "./"):
                path = message[message.index('Cookie:') + 1].replace("\r\n", "")
                writer.writelines([
                    b'HTTP/1.1 302 Found\r\n',
                    b'Content-Type:text/html; charset=utf-8\r\n',
                    b'Connection: close\r\n',
                    bytes('Location: ' + path[1:] + '\r\n', 'utf-8'),
                    b'\r\n'
                ])
                flag = True

        if flag:
            print("gg")
        elif os.path.exists(path):
            if os.path.isdir(path):
                body = [b'HTTP/1.1 200 OK\r\n', b'Content-Type:text/html; charset=utf-8\r\n',
                        b'Connection: close\r\n',
                        bytes('Set-Cookie: ' + path + '\r\n', 'utf-8'),
                        b'\r\n',
                        bytes('<html><head><title>Index of ' + str(path) + '</title></head>', 'utf-8')
                        ]

                body = body + [
                    b'<body bgcolor="white">',
                    bytes('<h1>Index of ' + str(path) + '</h1><hr>', 'utf-8'),
                    b'<pre>'
                ]
                print(os.listdir(path))
                for x in os.listdir(path):
                    body.append(bytes('<a href=' + str(posixpath.split(path)[-1]) + '/' + str(x) + '>' + str(x) + '</a><br>','utf-8'))

                body = body + [
                    b'</pre>'
                    b'<hr>'
                    b'</body></html>\r\n',
                    b'\r\n'
                ]

                writer.writelines(body)
            else:
                # 发文件啦
                size = os.path.getsize(path)
                file = open(path, 'rb')
                # start, end = 0, size - 1
                # if 'Range' in message:
                if 'Range:' in message:
                    start, end = message[message.index('Range:')+1].strip().strip('bytes=').split('-')
                    if start == "":
                        start = size - end
                    else:
                        if end == "":
                            end = size-1
                    start = int(start)
                    end = int(end)
                    writer.writelines([
                        b'HTTP/1.1 206 Partial Content\r\n',
                        bytes('Content-Type: ' + guess_type(path) + '\r\n', 'utf-8'),
                        b'Accept-Ranges: bytes\r\n',
                        bytes('Content-Range: ' + 'bytes %s-%s/%s\r\n' % (start, end, size), 'utf-8'),
                        b'\r\n'
                    ])
                    file.seek(start)
                    writer.write(file.read(end-start+1))

                else:
                    writer.writelines([
                        b'HTTP/1.1 200 OK\r\n',
                        b'Content-Type:text/html; charset=utf-8\r\n',
                        b'Connection: close\r\n',
                        bytes('Content-Length: ' + str(size) + '\r\n', 'utf-8'),
                        bytes('Content-Type: ' + guess_type(path) + '\r\n', 'utf-8'),
                        b'\r\n'
                    ])
                    writer.write(file.read())

        else:
            writer.writelines([
                b'HTTP/1.1 404 Not found\r\n',
                b'Content-Type:text/html; charset=utf-8\r\n',
                b'Connection: close\r\n',
                b'\r\n',
                b'<html><body>404 Not found<body></html>\r\n',
                b'\r\n'
            ])
    elif message[0] == "HEAD":
        if os.path.exists(path):
            if os.path.isdir(path):
                writer.writelines([
                    b'HTTP/1.1 200 OK\r\n',
                    b'Content-Type:text/html; charset=utf-8\r\n',
                    bytes('Set-Cookie: ' + path + '\r\n', 'utf-8'),
                    b'Connection: close\r\n',
                    b'\r\n'
                ])
            else:
                size = os.path.getsize(path)
                writer.writelines([
                    b'HTTP/1.1 200 OK\r\n',
                    b'Content-Type:text/html; charset=utf-8\r\n',
                    b'Connection: close\r\n',
                    bytes('Content-Length: ' + str(size) + '\r\n', 'utf-8'),
                    bytes('Content-Type: ' + guess_type(path) + '\r\n', 'utf-8'),
                    b'\r\n'
                ])

        else:
            writer.writelines([
                b'HTTP/1.1 404 Not found\r\n',
                b'Content-Type:text/html; charset=utf-8\r\n',
                b'Connection: close\r\n',
                b'\r\n',
                b'<html><body>404 Not found<body></html>\r\n',
                b'\r\n'
            ])
    else:
        writer.writelines([
            b'HTTP/1.1 405 Method Not Allowed\r\n',
            b'Content-Type:text/html; charset=utf-8\r\n',
            b'Connection: close\r\n',
            b'\r\n'
            b'<html><body>405 Method Not Allowed<body></html>\r\n',
            b'\r\n'
        ])

    await writer.drain()
    writer.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(dispatch, '127.0.0.1', 2333, )
    server = loop.run_until_complete(coro)
    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
