package demoTorReceiver;

import org.berndpruenster.netlayer.tor.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.util.concurrent.TimeUnit;

public class Main {
    public static void main(String[] args) {
        new TorReceiver();
    }

    // listen & log data received on our hidden service port 9999
    public static class TorReceiver {
        private static final Logger log = LoggerFactory.getLogger(TorReceiver.class);
        boolean waitingForInput = true;

        public TorReceiver() {
            try {
                String hsDir = System.getProperty("user.home") + "/.local/share/Bisq/btc_mainnet/tor/hiddenservice";
                Tor.setDefault(new ExternalTor(9051, "notrequired"));
                log.warn(Tor.getDefault().toString());
                int localPort = 9998;
                int servicePort = 9999;
                HiddenServiceSocket hiddenServiceSocket = new HiddenServiceSocket(localPort, hsDir, servicePort);
                hiddenServiceSocket.addReadyListener(torSock -> {
                    try {
                        log.info("Tor hidden service published!");
                        log.info(torSock.toString());
                        Socket socket = torSock.accept();
                        InetSocketAddress xyz = ((InetSocketAddress) socket.getRemoteSocketAddress());
                        log.info("new client connected on {} {}", xyz.getHostName(), xyz.getPort());
                        BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                        for (int n = 0; n < 10; n++) {
                            if (reader.ready()) {
                                String line = reader.readLine();
                                log.info("read from peer: {}", line);
                            }
                            TimeUnit.SECONDS.sleep(3);
                        }
                    } catch (final Exception e) {
                        log.error(e.toString());
                        e.printStackTrace();
                    }
                    waitingForInput = false;
                    return null;
                });

                while (waitingForInput) {
                    TimeUnit.SECONDS.sleep(3);
                }
            } catch (Exception | TorCtlException e) {
                log.warn(e.toString());
                e.printStackTrace();
            }
        }
    }
}
