#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/inotify.h>
#include <errno.h>
#include <time.h>
#include <pthread.h>

#define EVENT_SIZE (sizeof(struct inotify_event))
#define BUF_LEN (1024 * (EVENT_SIZE + 16))

typedef struct {
    char *config_path;
    void (*callback)(void);
    int wd;  // inotify watch descriptor
    int fd;  // inotify file descriptor
    int running;
    pthread_t thread;
} ConfigWatcher;

typedef struct {
    ConfigWatcher *watchers;
    int count;
    int capacity;
    int running;
    pthread_t thread;
} MultiConfigWatcher;

static void *watch_loop(void *arg) {
    ConfigWatcher *watcher = (ConfigWatcher *)arg;
    char buffer[BUF_LEN];
    int length, i = 0;
    
    while (watcher->running) {
        length = read(watcher->fd, buffer, BUF_LEN);
        
        if (length < 0) {
            if (errno == EINTR) continue;
            perror("read");
            break;
        }
        
        while (i < length) {
            struct inotify_event *event = (struct inotify_event *)&buffer[i];
            
            if (event->mask & IN_MODIFY) {
                // Small delay to ensure file write is complete
                usleep(100000);  // 100ms
                
                if (watcher->callback) {
                    watcher->callback();
                }
            }
            
            i += EVENT_SIZE + event->len;
        }
        
        i = 0;
    }
    
    return NULL;
}

ConfigWatcher *config_watcher_create(const char *config_path, void (*callback)(void)) {
    ConfigWatcher *watcher = malloc(sizeof(ConfigWatcher));
    if (!watcher) return NULL;
    
    watcher->config_path = strdup(config_path);
    watcher->callback = callback;
    watcher->running = 0;
    
    // Initialize inotify
    watcher->fd = inotify_init();
    if (watcher->fd < 0) {
        perror("inotify_init");
        free(watcher->config_path);
        free(watcher);
        return NULL;
    }
    
    // Add watch
    watcher->wd = inotify_add_watch(watcher->fd, config_path, IN_MODIFY);
    if (watcher->wd < 0) {
        perror("inotify_add_watch");
        close(watcher->fd);
        free(watcher->config_path);
        free(watcher);
        return NULL;
    }
    
    return watcher;
}

void config_watcher_start(ConfigWatcher *watcher) {
    if (!watcher || watcher->running) return;
    
    watcher->running = 1;
    if (pthread_create(&watcher->thread, NULL, watch_loop, watcher) != 0) {
        perror("pthread_create");
        watcher->running = 0;
    }
}

void config_watcher_stop(ConfigWatcher *watcher) {
    if (!watcher || !watcher->running) return;
    
    watcher->running = 0;
    pthread_join(watcher->thread, NULL);
}

void config_watcher_destroy(ConfigWatcher *watcher) {
    if (!watcher) return;
    
    config_watcher_stop(watcher);
    
    if (watcher->wd >= 0) {
        inotify_rm_watch(watcher->fd, watcher->wd);
    }
    
    if (watcher->fd >= 0) {
        close(watcher->fd);
    }
    
    free(watcher->config_path);
    free(watcher);
}

// Test implementation
void test_callback(void) {
    printf("Configuration file changed!\n");
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <config_file>\n", argv[0]);
        return 1;
    }
    
    ConfigWatcher *watcher = config_watcher_create(argv[1], test_callback);
    if (!watcher) {
        fprintf(stderr, "Failed to create config watcher\n");
        return 1;
    }
    
    printf("Watching %s for changes...\n", argv[1]);
    printf("Press Ctrl+C to stop\n");
    
    config_watcher_start(watcher);
    
    // Wait for interrupt
    while (1) {
        sleep(1);
    }
    
    config_watcher_destroy(watcher);
    return 0;
}
