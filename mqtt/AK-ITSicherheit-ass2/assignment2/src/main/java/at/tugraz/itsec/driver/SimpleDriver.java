package at.tugraz.itsec.driver;

import java.util.List;

import de.learnlib.drivers.api.TestDriver;
import de.learnlib.drivers.reflect.ConcreteMethodInput;
import de.learnlib.mapper.api.SULMapper;
import net.automatalib.words.Alphabet;
import net.automatalib.words.impl.Alphabets;

public class SimpleDriver extends TestDriver<String, String, ConcreteMethodInput, Object>{
    private Alphabet<String> alphabet;

    public SimpleDriver(SULMapper<String, String, ConcreteMethodInput, Object> mapper) {
        super(mapper);
    }

    public void addAlphabet(List<String> inputs){
        alphabet = Alphabets.fromCollection(inputs);
    }

    public Alphabet<String> getAlphabet(){ return this.alphabet;}

}