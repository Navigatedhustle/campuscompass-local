/* Application-level network guard. No host firewall or interface changes.
 * Limits dynamically linked libc connections to loopback/Unix sockets.
 * Not a sandbox against hostile binaries issuing direct syscalls. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <string.h>
static int allowed(const struct sockaddr *a){
 if(!a)return 1;
 if(a->sa_family==AF_UNIX)return 1;
 if(a->sa_family==AF_INET)return (ntohl(((const struct sockaddr_in*)a)->sin_addr.s_addr)>>24)==127;
 if(a->sa_family==AF_INET6)return IN6_IS_ADDR_LOOPBACK(&((const struct sockaddr_in6*)a)->sin6_addr);
 return 0;
}
int connect(int fd,const struct sockaddr *a,socklen_t n){
 if(!allowed(a)){errno=EACCES;return -1;}
 int(*real)(int,const struct sockaddr*,socklen_t)=dlsym(RTLD_NEXT,"connect");return real(fd,a,n);
}
ssize_t sendto(int fd,const void *buf,size_t n,int flags,const struct sockaddr *a,socklen_t len){
 if(!allowed(a)){errno=EACCES;return -1;}
 ssize_t(*real)(int,const void*,size_t,int,const struct sockaddr*,socklen_t)=dlsym(RTLD_NEXT,"sendto");return real(fd,buf,n,flags,a,len);
}
ssize_t sendmsg(int fd,const struct msghdr *msg,int flags){
 if(msg->msg_name&&!allowed(msg->msg_name)){errno=EACCES;return -1;}
 ssize_t(*real)(int,const struct msghdr*,int)=dlsym(RTLD_NEXT,"sendmsg");return real(fd,msg,flags);
}
int getaddrinfo(const char *host,const char *service,const struct addrinfo *hints,struct addrinfo **result){
 if(host&&strcmp(host,"localhost")&&strcmp(host,"127.0.0.1")&&strcmp(host,"::1")){return EAI_NONAME;}
 int(*real)(const char*,const char*,const struct addrinfo*,struct addrinfo**)=dlsym(RTLD_NEXT,"getaddrinfo");return real(host,service,hints,result);
}
