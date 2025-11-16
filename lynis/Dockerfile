FROM ubuntu:latest

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Lynis and required dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends lynis curl bash wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Pre-configure Postfix to avoid interactive prompts (if it gets installed later)
RUN echo "postfix postfix/mailname string localhost" | debconf-set-selections && \
    echo "postfix postfix/main_mailer_type string 'Local only'" | debconf-set-selections

# Create directory for Lynis plugin
RUN mkdir -p /usr/local/lynis/plugins

# Copy TrikuSec plugin
COPY trikusec-lynis-plugin/plugin_trikusec_phase1 /usr/local/lynis/plugins/plugin_trikusec_phase1
RUN chmod +x /usr/local/lynis/plugins/plugin_trikusec_phase1

# Create test directory
RUN mkdir -p /test

# Copy test script
COPY lynis/run-lynis-test.sh /test/run-lynis-test.sh
RUN chmod +x /test/run-lynis-test.sh

# Set working directory
WORKDIR /test

# Default command
CMD ["/bin/bash"]

