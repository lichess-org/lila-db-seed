import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Base64;
import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import org.mindrot.BCrypt;

public class App {
  static String secret;

  public static void main(String[] args) throws Exception {

    secret = args[0];

    var in = System.in.readAllBytes();

    byte[] salt = new byte[16];
    SecureRandom.getInstanceStrong().nextBytes(salt);

    byte[] digest = MessageDigest.getInstance("SHA-512").digest(in);

    byte[] hash = BCrypt.hashpwRaw(digest, 'a', 10, salt);

    byte[] aesHash = aesCtsEncrypt(salt, hash);

    System.out.write(68);
    System.out.write(68); // 6868 indicates success to spamdb.py

    System.out.write(salt);
    System.out.write(aesHash);
  }

  static byte[] aesCtsEncrypt(byte[] iv, byte[] buf) throws Exception {
    var c = Cipher.getInstance("AES/CTS/NoPadding");

    c.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(Base64.getDecoder().decode(secret), "AES"),
        new IvParameterSpec(iv));

    return c.doFinal(buf);
  }
}
