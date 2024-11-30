import { Button, Flex, Grid, Heading, Input, Textarea } from "@chakra-ui/react";
import Navbar from "../../components/Navbar/Navbar";
import InputBox from "../../components/InputBox/InputBox";
import "./styles.css";
import AgentBox from "../../components/AgentBox/AgentBox";
import { useEffect, useState } from "react";
import { Agent } from "../../utils/types";
import AgentCode from "../../components/AgentCode/AgentCode";
import axios from "axios";

function Home() {
  const numbers = [2, 23, 4, 63, 7, 19, 42, 0, -24];

  const [agents, setAgents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchAgents();
  }, []);

  // Función para obtener los agentes
  const fetchAgents = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get("http://localhost:8000/appAgent/agent/"); // Reemplaza esta URL con la real de tu API
      setAgents(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const [selectedAgents, setSelectedAgents] = useState<Agent[]>([]);
  const [isNativeCode, setIsNativeCode] = useState(true);

  const addAgent = (agent: Agent) => {
    console.log("agente añadido");
    setSelectedAgents([...selectedAgents, agent]);
  };

  const removeAgent = (index: number) => {
    console.log("agente removido");
    setSelectedAgents(selectedAgents.filter((_, i) => i !== index));
  };

  return (
    <>
      <Flex direction="column" minHeight="100vh">
        <Navbar />
        <Grid templateColumns="150px 6fr 400px">
          <Flex bg="gray.300" direction="column" align="center" p="30px">
            <Heading size="4xl" color="gray.600" paddingBottom="30px">
              Input
            </Heading>
            {numbers.map((item) => (
              <InputBox num={item} />
            ))}
          </Flex>
          <Flex bg="gray.100" p="30px" direction="column">
            <Heading
              size="5xl"
              color="gray.600"
              paddingBottom="20px"
              textAlign="center"
            >
              Agents
            </Heading>
            <Flex h="fit" flexWrap="wrap" p="40px" gap="30px" justify="center">
              {isLoading ? (
                <Heading>Cargando ...</Heading>
              ) : (
                agents.map((agent) => (
                  <Flex
                    align="center"
                    justify="space-between"
                    width="100%"
                    borderBottom="1px solid #d4d4d8"
                    padding="15px 0"
                  >
                    <AgentBox agent={agent}></AgentBox>
                    <Button
                      variant="outline"
                      color="green"
                      fontSize="25px"
                      onClick={() => addAgent(agent)}
                    >
                      Add
                    </Button>
                  </Flex>
                ))
              )}
            </Flex>
          </Flex>
          <Flex bg="gray.300" direction="column" p="30px">
            <Heading
              size="4xl"
              h="fit"
              color="gray.600"
              paddingBottom="30px"
              textAlign="center"
            >
              Code
            </Heading>
            {isNativeCode ? (
              <Flex>
                <Button
                  borderBottomRadius="0"
                  borderTopRadius="10px"
                  marginStart="20px"
                  variant="subtle"
                  bg="white"
                  color="gray"
                  fontSize="25px"
                  onClick={() => setIsNativeCode(true)}
                >
                  Native
                </Button>
                <Button
                  borderTopRadius="10px"
                  borderBottomRadius="0"
                  marginStart="10px"
                  variant="subtle"
                  bg="gray.200"
                  color="gray"
                  fontSize="25px"
                  onClick={() => setIsNativeCode(false)}
                >
                  by Agents
                </Button>
              </Flex>
            ) : (
              <>
                <Flex align='center' marginBottom='30px'>
                  <Heading color='green' marginEnd='10px'>Nombre:</Heading>
                  <Input color='black'>
                  </Input>
                </Flex>
                <Flex>
                  <Button
                    borderBottomRadius="0"
                    borderTopRadius="10px"
                    marginStart="20px"
                    variant="subtle"
                    bg="gray.200"
                    color="gray"
                    fontSize="25px"
                    onClick={() => setIsNativeCode(true)}
                  >
                    Native
                  </Button>
                  <Button
                    borderTopRadius="10px"
                    borderBottomRadius="0"
                    marginStart="10px"
                    variant="subtle"
                    bg="white"
                    color="gray"
                    fontSize="25px"
                    onClick={() => setIsNativeCode(false)}
                  >
                    by Agents
                  </Button>
                </Flex>
              </>
            )}
            <Flex
              bg="white"
              borderRadius="20px"
              h="500px"
              direction="column"
              align="center"
            >
              {isNativeCode ? (
                <>
                  <Textarea
                    placeholder="Enter native code here..."
                    height="100%"
                    width="100%"
                    borderRadius="20px"
                    textWrap="nowrap"
                    color="black"
                  />
                </>
              ) : (
                selectedAgents.map((agent, index) => (
                  <Flex
                    align="center"
                    justify="space-between"
                    borderBottom="1px solid #d4d4d8"
                    width="90%"
                    padding="15px 0"
                  >
                    <AgentCode index={index} agent={agent}></AgentCode>
                    <Button
                      variant="outline"
                      color="red"
                      fontSize="25px"
                      onClick={() => removeAgent(index)}
                    >
                      X
                    </Button>
                  </Flex>
                ))
              )}
            </Flex>
            <Flex margin="20px">
              <Button>Create Agent</Button>
              {!isNativeCode && (
                <Button marginStart="10px" colorPalette="blue">
                  Run Solution
                </Button>
              )}
            </Flex>
          </Flex>
        </Grid>
      </Flex>
    </>
  );
}

export default Home;
