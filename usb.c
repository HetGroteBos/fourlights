/* Compile with -lusb -lm -std=gnu99 usb.c -o usb */ 

#include <libusb-1.0/libusb.h>

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <math.h>

/* Following two values taken from ola (opendmx.net) */
#define URB_TIMEOUT_MS 500
#define UDMX_SET_CHANNEL_RANGE 0x0002

int write_buf(libusb_device_handle *h, unsigned char* dat, int size) {
    long r = libusb_control_transfer(h,
            LIBUSB_REQUEST_TYPE_VENDOR | LIBUSB_RECIPIENT_DEVICE |
            LIBUSB_ENDPOINT_OUT, UDMX_SET_CHANNEL_RANGE,
            size, 0, dat, size, URB_TIMEOUT_MS);
    return r >= 0;
}

libusb_device_handle * open_dmx(void) {
    libusb_device_handle *h = NULL;
    libusb_device **dl;
    size_t dc;
    int f = 0;
    unsigned int i = 0;

    if (libusb_init(NULL)) {
        perror("libusb_init");
        goto aexit;
    }

    dc = libusb_get_device_list(NULL, &dl);

    for (i = 0; i < dc; i++) {
        struct libusb_device_descriptor dd;
        libusb_get_device_descriptor(dl[i], &dd);

        printf("Vendor: 0x%4x, Product: 0x%4x\n", dd.idVendor,
            dd.idProduct);

        if ((dd.idVendor == 0x3eb) && (dd.idProduct = 0x8888)) {
            if(libusb_open(dl[i], &h)) {
                perror("libusb_open");
                goto aexit;
            }
            f = 1;
            printf("Found!\n");
            break;
        }
    }

    if (!f) {
        printf("Not found!\n");
        goto aexit;
    }

    if (libusb_claim_interface(h, 0)) {
        perror("libusb_claim_interface");
        goto aexit;
    }

    return h;

aexit:
    if (h)
        libusb_close(h);
    libusb_exit(NULL);
}

void close_dmx(libusb_device_handle *h) {
    if (h) {
        libusb_release_interface(h, 0);
        libusb_close(h);
    }
    libusb_exit(NULL);

    return;
}

void sin_demo(libusb_device_handle *h, unsigned char *buf, int bufsize) {
    for (int k = 0; k < 100; k++) {
        for (int c = 0; c < 360; c++) {
            for (int i = 0; i < bufsize; i += 3) {
                double r, g, b = 0;

                r = fabs(sin(((c / 180. * M_PI) + (k % 3) * 0.5 * M_PI)));
                g = fabs(sin(((c / 180. * M_PI) + (k % 3 + 1) * 0.5 * M_PI)));
                b = fabs(sin(((c / 180. * M_PI) + (k % 3 + 2) * 0.5 * M_PI)));

                buf[i] = r * 55;
                buf[i + 1] = g * 55;
                buf[i + 2] = b * 55;

                write_buf(h, buf, bufsize);
            }
            usleep(20000);
        }
    }
}

void demo(libusb_device_handle *h) {
    int bufsize = 3;
    unsigned char *buf = calloc(bufsize, sizeof(unsigned char));

    sin_demo(h, buf, bufsize);

    free(buf);
    return;
}

int main() {
    libusb_device_handle *h = NULL;

    h = open_dmx();

    demo(h);

    close_dmx(h);
}
