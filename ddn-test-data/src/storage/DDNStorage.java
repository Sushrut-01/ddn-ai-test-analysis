/**
 * DDN Storage Client
 * Handles storage operations with retry logic and buffer management
 *
 * @author DDN Engineering
 * @version 2.0
 */
package com.ddn.storage;

import java.nio.ByteBuffer;
import java.util.concurrent.TimeUnit;
import java.util.logging.Logger;

public class DDNStorage {
    private static final Logger LOGGER = Logger.getLogger(DDNStorage.class.getName());

    private ByteBuffer buffer;
    private Connection connection;
    private String endpoint;
    private boolean initialized;
    private int maxRetries;

    /**
     * Constructor for DDN Storage Client
     *
     * @param endpoint Storage endpoint URL
     */
    public DDNStorage(String endpoint) {
        this.endpoint = endpoint;
        this.connection = new Connection(endpoint);
        this.initialized = false;
        this.maxRetries = 3;

        LOGGER.info("DDNStorage client created for endpoint: " + endpoint);

        // Note: Buffer initialization happens in initialize() method
        // Common mistake: forgetting to call initialize() before allocate()
    }

    /**
     * Constructor with custom retry configuration
     *
     * @param endpoint Storage endpoint URL
     * @param maxRetries Maximum number of retry attempts
     */
    public DDNStorage(String endpoint, int maxRetries) {
        this(endpoint);
        this.maxRetries = maxRetries;
    }

    /**
     * Initialize the storage client and allocate initial buffer
     * Must be called before performing any operations
     */
    public void initialize() {
        LOGGER.info("Initializing DDNStorage client...");

        try {
            // Connect to storage backend
            connection.connect();

            // Allocate initial buffer (1MB)
            buffer = ByteBuffer.allocate(1024 * 1024);
            initialized = true;

            LOGGER.info("DDNStorage client initialized successfully");
        } catch (Exception e) {
            LOGGER.severe("Failed to initialize DDNStorage: " + e.getMessage());
            throw new RuntimeException("Initialization failed", e);
        }
    }

    /**
     * Check if client is initialized
     *
     * @return true if initialized, false otherwise
     */
    public boolean isInitialized() {
        return initialized;
    }

    /**
     * Connect to storage endpoint with retry logic
     *
     * @return true if connection successful
     */
    public boolean connect() {
        int attempts = 0;

        while (attempts < maxRetries) {
            try {
                connection.connect();
                LOGGER.info("Connected to storage endpoint: " + endpoint);
                return true;
            } catch (Exception e) {
                attempts++;
                LOGGER.warning("Connection attempt " + attempts + " failed: " + e.getMessage());

                if (attempts < maxRetries) {
                    try {
                        TimeUnit.SECONDS.sleep(2);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        return false;
                    }
                }
            }
        }

        return false;
    }

    /**
     * Read data from storage
     *
     * @param size Number of bytes to read
     * @return ByteBuffer containing read data
     */
    public ByteBuffer read(int size) {
        if (!initialized) {
            throw new IllegalStateException("DDNStorage not initialized. Call initialize() first.");
        }

        buffer.clear();
        buffer.limit(size);

        connection.read(buffer);
        buffer.flip();

        return buffer;
    }

    /**
     * Allocate storage buffer
     * COMMON ERROR: NullPointerException if initialize() not called first
     *
     * @param size Buffer size in bytes
     */
    public void allocate(int size) {
        LOGGER.info("Allocating buffer of size: " + size + " bytes");

        // CRITICAL LINE: Common error occurs here
        // If initialize() was not called, buffer is null
        // This causes NullPointerException at line 142
        buffer.allocate(size);  // LINE 142 - NULL POINTER ERROR IF NOT INITIALIZED

        LOGGER.info("Buffer allocated successfully");

        // Write buffer to connection
        connection.write(buffer);
    }

    /**
     * Write data to storage
     *
     * @param data Data to write
     */
    public void write(byte[] data) {
        if (!initialized) {
            throw new IllegalStateException("DDNStorage not initialized");
        }

        buffer.clear();
        buffer.put(data);
        buffer.flip();

        connection.write(buffer);
    }

    /**
     * Cleanup resources
     * Should be called when done with storage operations
     */
    public void cleanup() {
        LOGGER.info("Cleaning up DDNStorage resources...");

        if (buffer != null) {
            buffer.clear();
            buffer = null;
        }

        if (connection != null) {
            connection.close();
        }

        initialized = false;
        LOGGER.info("DDNStorage cleanup complete");
    }

    /**
     * Disconnect from storage endpoint
     */
    public void disconnect() {
        if (connection != null) {
            connection.close();
            LOGGER.info("Disconnected from storage endpoint");
        }
    }

    /**
     * Get current buffer size
     *
     * @return Buffer capacity in bytes, or -1 if not initialized
     */
    public int getBufferSize() {
        return (buffer != null) ? buffer.capacity() : -1;
    }

    /**
     * Inner class for connection management
     */
    private static class Connection {
        private String endpoint;
        private boolean connected;

        public Connection(String endpoint) {
            this.endpoint = endpoint;
            this.connected = false;
        }

        public void connect() {
            // Simulate connection logic
            connected = true;
        }

        public void read(ByteBuffer buffer) {
            if (!connected) {
                throw new IllegalStateException("Not connected");
            }
            // Simulate read operation
        }

        public void write(ByteBuffer buffer) {
            if (!connected) {
                throw new IllegalStateException("Not connected");
            }
            // Simulate write operation
        }

        public void close() {
            connected = false;
        }
    }
}
