package demoTorSender;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.TimeUnit;

public class Main {
    private static final Logger log = LoggerFactory.getLogger(Main.class);
    public static void main(String[] args) {
        // user can supply command line argument containing onion:port to send to
        new TorSender(args.length > 0 ? args[0] : "xk7q7muaqqqxahttp5r4y3e65x6ffr24ahcpk2pvpttxxyo375sbxxyd.onion:9999");
    }

    static class TorSender {
        public TorSender(String firstParam) {
            String[] parts = firstParam.split(":");
            if (parts.length != 2) {
                log.warn("ERROR command line argument should be in the format of xxxxxxxx.onion:port");
                return;
            }
            String connectToOnion = parts[0];
            int connectToPort = Integer.parseInt(parts[1]);
            String textToSend = "hello world!" + System.lineSeparator();
            try {
                TorConnection torConnection = new TorConnection();
                waitFor(5);
                log.info("connecting to {}:{}", connectToOnion, connectToPort);
                Socket sock = torConnection.createSocket(connectToOnion, connectToPort);
                log.info(sock.toString());
                waitFor(1);
                log.info("writing to socket...{}", textToSend);
                sock.getOutputStream().write(textToSend.getBytes(StandardCharsets.UTF_8));
                waitFor(2);
                sock.close();
                log.info("closed socket");
            } catch (Exception ex) {
                log.warn(ex.toString());
                ex.printStackTrace();
            } finally {
                log.info("Finished.");
            }
        }

        private void waitFor(int limit) {
            try {
                for (int n=0; n < limit; n++) {
                    log.info("waiting...");
                    TimeUnit.SECONDS.sleep(3);
                }
            } catch (InterruptedException e) {
                log.warn(e.toString());
            }
        }
    }
}
