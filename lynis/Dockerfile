FROM alpine:latest

# Install Lynis and required dependencies
RUN apk add --no-cache lynis curl bash

# Create directory for Lynis plugin
RUN mkdir -p /usr/local/lynis/plugins

# Copy Compleasy plugin
COPY compleasy-lynis-plugin/plugin_compleasy_phase1 /usr/local/lynis/plugins/plugin_compleasy_phase1
RUN chmod +x /usr/local/lynis/plugins/plugin_compleasy_phase1

# Create test directory
RUN mkdir -p /test

# Copy test script
COPY lynis/run-lynis-test.sh /test/run-lynis-test.sh
RUN chmod +x /test/run-lynis-test.sh

# Set working directory
WORKDIR /test

# Default command
CMD ["/bin/sh"]

