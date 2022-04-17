package demoTorSender;

import org.berndpruenster.netlayer.tor.*;

import java.io.IOException;
import java.net.Socket;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TorConnection {
    private static final Logger log = LoggerFactory.getLogger(TorConnection.class);

    public TorConnection() {
        String hsDir = System.getProperty("user.home") + "/.local/share/Bisq.old/btc_mainnet/tor/hiddenservice";
        try {
            Tor.setDefault(new ExternalTor(9051, "notrequired"));
        } catch (TorCtlException e) {
            e.printStackTrace();
        }
        log.warn(Tor.getDefault().toString());
        int localPort = 9990;
        int servicePort = 9991;
        log.info(hsDir);
        HiddenServiceSocket hiddenServiceSocket = new HiddenServiceSocket(localPort, hsDir, servicePort);
        hiddenServiceSocket.addReadyListener(socket -> {
            try {
                log.info("Tor hidden service published!");
                log.info(socket.toString());
            } catch (final Exception e) {
                log.error(e.toString());
                e.printStackTrace();
            }
            return null;
        });
    }

    public Socket createSocket(String peer, int peerPort) throws IOException {
        return new TorSocket(peer, peerPort, null);
    }
}