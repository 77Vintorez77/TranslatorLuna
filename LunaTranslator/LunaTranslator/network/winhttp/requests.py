
from winhttp import * 
from network.requests_common import *
class Session(Sessionbase):
 
     
    def raise_for_status(self):
        error=GetLastError()
        if error:
            raise WinhttpException(error)
      
    
    def _getheaders(self,hreq):
        dwSize=DWORD()
        WinHttpQueryHeaders(hreq, WINHTTP_QUERY_RAW_HEADERS_CRLF, WINHTTP_HEADER_NAME_BY_INDEX, None, pointer(dwSize), WINHTTP_NO_HEADER_INDEX);
        
        pszCookies=create_unicode_buffer(dwSize.value//2+1)
        succ=WinHttpQueryHeaders(hreq, WINHTTP_QUERY_RAW_HEADERS_CRLF, WINHTTP_HEADER_NAME_BY_INDEX, pszCookies , pointer(dwSize), WINHTTP_NO_HEADER_INDEX)
        if succ==0:
            return ''
        return (pszCookies.value)
    def _getStatusCode(self,hreq):
        dwSize=DWORD(sizeof(DWORD))
        dwStatusCode=DWORD()
        bResults = WinHttpQueryHeaders( hreq,   WINHTTP_QUERY_STATUS_CODE |   WINHTTP_QUERY_FLAG_NUMBER,  None, 
                                      pointer(dwStatusCode), 
                                      pointer(dwSize), 
                                      None )
        if bResults==0:
            self.raise_for_status()
        return dwStatusCode.value
     
    def _set_proxy(self,hsess,proxy):
        if proxy:
            winhttpsetproxy(hsess,proxy)
    
    def request_impl(self,
        method,scheme,server,port,param,url,headers,dataptr,datalen,proxy,stream,verify):
          
        flag=WINHTTP_FLAG_SECURE if scheme=='https' else 0
        #print(server,port,param,dataptr)
        headers='\r\n'.join(headers) 
        
        if self.hSession==0 or proxy!=self.proxy:
            self.proxy=proxy
            self.hSession=AutoWinHttpHandle(WinHttpOpen(self.UA,WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,WINHTTP_NO_PROXY_NAME,WINHTTP_NO_PROXY_BYPASS,0))
            if self.hSession==0:
                raise WinhttpException(GetLastError())  
        
        hConnect=AutoWinHttpHandle(WinHttpConnect(self.hSession,server,port,0))
        if hConnect==0:
            raise WinhttpException(GetLastError())  
        hRequest=AutoWinHttpHandle(WinHttpOpenRequest( hConnect ,method,param,None,WINHTTP_NO_REFERER,WINHTTP_DEFAULT_ACCEPT_TYPES,flag) )
    
        if hRequest==0:
            raise WinhttpException(GetLastError())
        self._set_proxy(hRequest,proxy) 
        
        succ=WinHttpSendRequest(hRequest,headers,-1,dataptr,datalen,datalen,None)
        if succ==0:
            raise WinhttpException(GetLastError())
        
        succ=WinHttpReceiveResponse(hRequest,None)
        if succ==0:
            raise WinhttpException(GetLastError())
        
        self._update_header_cookie(self._getheaders(hRequest))
        
        self.status_code=self._getStatusCode(hRequest)
        if stream:
            self.hconn=hConnect
            self.hreq=hRequest
            return self
        availableSize=DWORD()
        downloadedSize=DWORD()
        downloadeddata=b''
        while True:
            succ=WinHttpQueryDataAvailable(hRequest,pointer(availableSize))
            if succ==0:
                raise WinhttpException(GetLastError())
            if availableSize.value==0:
                break
            buff=create_string_buffer(availableSize.value)
            #这里可以做成流式的
            succ=WinHttpReadData(hRequest,buff,availableSize,pointer(downloadedSize))
            if succ==0:raise WinhttpException(GetLastError())
            downloadeddata+=buff[:downloadedSize.value]
        self.content=downloadeddata
        #print(self.text)
        
        return self
    def iter_content(self,chunk_size=1024):
        downloadedSize=DWORD()
        buff=create_string_buffer(chunk_size)
            
        while True:
            succ=WinHttpReadData(self.hreq,buff,chunk_size,pointer(downloadedSize))
            if succ==0:raise WinhttpException(GetLastError())
            if downloadedSize.value==0:
                del self.hreq
                del self.hconn
                break
            yield buff[:downloadedSize.value]
    
Sessionimpl[0]=Session
if __name__=='__main__':
    pass
     