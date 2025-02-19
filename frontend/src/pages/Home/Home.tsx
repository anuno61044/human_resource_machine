import {
  Box,
  Button,
  Flex,
  Grid,
  Heading,
  Input,
  Select,
  Separator,
  Textarea,
} from "@chakra-ui/react";
import Navbar from "../../components/Navbar/Navbar";
import InputBox from "../../components/InputBox/InputBox";
import "./styles.css";
import AgentBox from "../../components/AgentBox/AgentBox";
import { useEffect, useState } from "react";
import { Agent, Functionality } from "../../utils/types";
import AgentCode from "../../components/AgentCode/AgentCode";
import axios from "axios";
import { MultiSelect } from "react-multi-select-component";
import { Option } from "react-multi-select-component";
import InitialAgentBox from "../../components/InitialAgentBox/InitialAgentBox";
import InitialAgentCode from "../../components/InitialAgentCode/InitialAgentCode";
import InitialAgentCodeMemory from "../../components/InitialAgentCode/InitialAgentCodeMemory";

function Home() {
  const initialAgents = [
    {
      id: 0,
      name: "inbox",
      memory: 0,
      pythonCode: "",
      _type: false,
      function: [],
    },
    {
      id: 0,
      name: "outbox",
      memory: 0,
      pythonCode: "",
      _type: false,
      function: [],
    },
    {
      id: -1,
      name: "copyto",
      memory: 0,
      pythonCode: "",
      _type: false,
      function: [],
    },
    {
      id: -1,
      name: "copyfrom",
      memory: 0,
      pythonCode: "",
      _type: false,
      function: [],
    },
    {
      id: -1,
      name: "jump",
      memory: 0,
      pythonCode: "",
      _type: false,
      function: [],
    },
    {
      id: -1,
      name: "jez",
      memory: 0,
      pythonCode: "",
      _type: false,
      function: [],
    },
    {
      id: -1,
      name: "jlz",
      memory: 0,
      pythonCode: "",
      _type: false,
      function: [],
    },
    {
      id: -1,
      name: "jgz",
      memory: 0,
      pythonCode: "",
      _type: false,
      function: [],
    },
  ];

  const [numbers, setNumbers] = useState<string[]>([]);
  const [numberInput, setNumberInput] = useState<string>("0");
  const [output, setOutput] = useState<number[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [functionalities, setFunctionalities] = useState<Functionality[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedAgents, setSelectedAgents] = useState<Agent[]>([]);
  const [isNativeCode, setIsNativeCode] = useState(true);
  const [selectedValues, setSelectedValues] = useState<Option[]>([]);
  const [agentShow, setAgentShow] = useState<Agent>({
    id: 0,
    name: "",
    memory: 0,
    pythonCode: "",
    _type: true,
    function: [],
  });

  useEffect(() => {
    fetchAgents();
    fetchFunctionalities();
  }, []);

  // Función para obtener los agentes
  const fetchFunctionalities = async () => {
    try {
      const response = await axios.get(
        "http://localhost:8000/appFunctionality/functionality/"
      ); // Reemplaza esta URL con la real de tu API
      setFunctionalities(response.data);
    } catch (err) {
      console.error(err);
    }
  };

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

  // Crear o editar un agente
  const handleSubmitAgent = async () => {
    // Handle Name
    let name = agentShow.name;

    // Handle Code
    let pythonCode = "";
    if (isNativeCode) {
      pythonCode = agentShow.pythonCode;
    } else {
      pythonCode = "[";
      for (const ag of selectedAgents) {
        if (ag.id == 0) {
          pythonCode += `{
            \"type\":\"initial\",
            \"name\":\"${ag.name}\"
          },`;
        } else if (ag.id == -1) {
          pythonCode += `{
            \"type\":\"created\",
            \"name\":\"${ag.name}\",
            \"target\":${ag.memory}
          },`;
        } else {
          pythonCode += `{
            \"type\":\"user\",
            \"id\":${ag.id}
          },`;
        }
      }
      pythonCode = pythonCode.slice(0, -1);
      pythonCode += "]";
    }
    console.log(pythonCode)

    // Handle functionalities
    const functions = selectedValues.map((f) => f.value.name);

    if (agentShow.id == 0) {
      try {
        await axios.post("http://localhost:8000/appAgent/agent/create/", {
          name: name,
          memory: 0,
          pythonCode: pythonCode,
          _type: isNativeCode,
          function: functions,
        });
      } catch (err) {
        console.error(err);
      } finally {
        fetchAgents();
      }
    } else {
      try {
        await axios.put(
          `http://localhost:8000/appAgent/agent/${agentShow.name}`,
          {
            name: name,
            memory: agentShow.memory,
            pythonCode: pythonCode,
            _type: isNativeCode,
            function: functions,
          }
        );
      } catch (err) {
        console.error(err);
      } finally {
        fetchAgents();
        setAgentShow({
          id: 0,
          name: "",
          memory: 0,
          pythonCode: "",
          _type: true,
          function: [],
        });
      }
    }
  };

  const handleEditAgent = async (agent: Agent) => {
    setAgentShow(agent);

    setSelectedValues(
      agent.function.map((e) => ({
        label: functionalities.find((f) => f.id == e).name,
        value: functionalities.find((f) => f.id == e),
      }))
    );

    if (agent._type) {
      setIsNativeCode(true);
      return;
    }

    setIsNativeCode(false);
    const code_agents = JSON.parse(agent.pythonCode);
    console.log(code_agents);
    let agent_arr:Agent[] = []
    for (const ag of code_agents) {
      if (ag['type']=='initial') {
        agent_arr = [...agent_arr,{
          id:0,
          pythonCode:'',
          memory:0,
          _type:true,
          name:ag['name'],
          function:[]
        }]
      }
      else if (ag['type']=='created') {
        agent_arr = [...agent_arr,{
          id:-1,
          pythonCode:'',
          memory:ag['target'],
          _type:true,
          name:ag['name'],
          function:[]
        }]
      }
      else {
        let agent_find = agents.find(a => a.id == ag['id'])

        if (agent_find) {
          agent_arr = [...agent_arr, agent_find];
        } else {
          throw new Error(`No se encontró el agente con id ${ag['id']}`);
        }
      }
    }

    setSelectedAgents(agent_arr)
  };

  const handleDeleteAgent = async (agent_name: string) => {
    try {
      await axios.delete(`http://localhost:8000/appAgent/agent/${agent_name}`);
    } catch (err) {
      console.error(err);
    } finally {
      fetchAgents();
    }
  };

  const handleSolution = async () => {

    // Handle Code
    let pythonCode = "";
    if (isNativeCode) {
      pythonCode = agentShow.pythonCode;
    } else {
      pythonCode = "[";
      for (const ag of selectedAgents) {
        if (ag.id == 0) {
          pythonCode += `{
            \"type\":\"initial\",
            \"name\":\"${ag.name}\"
          },`;
        } else if (ag.id == -1) {
          pythonCode += `{
            \"type\":\"initial\",
            \"name\":\"${ag.name}\",
            \"target\":${ag.memory}
          },`;
        } else {
          pythonCode += `{
            \"type\":\"user\",
            \"name\":"${ag.name}"
          },`;
        }
      }
      pythonCode = pythonCode.slice(0, -1);
      pythonCode += "]";
    }
    console.log(pythonCode)

    let input = '['

    for (const c of numbers) {
      input += c + ','
    }
    input = input.slice(0,-1)
    input += ']'
    console.log(input)

    try {
      const response = await axios.post("http://localhost:8000/appSolution/solution/", {
        input: input,
        agents: pythonCode
      });
      setOutput(JSON.parse(response.data))
      console.log(response.data)
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <>
      <Flex direction="column" minHeight="100vh">
        <Navbar />

        <Grid templateColumns="150px auto 400px 150px">
          {/* INPUT AREA */}
          <Flex bg="gray.300" direction="column" align="center" p="30px">
            <Heading size="4xl" color="gray.600" paddingBottom="30px">
              Input
            </Heading>
            <Separator marginBottom="20px" />
            <Flex marginBottom="20px" direction="column" align="center">
              <Input
                type="number"
                w="70px"
                border="1px solid #6e6d6d8c"
                color="black"
                value={numberInput}
                onChange={(e) => setNumberInput(e.target.value)}
              />
              <Flex marginTop="10px">
                <Button
                  w="45px"
                  color="white"
                  colorPalette="green"
                  fontSize="20px"
                  onClick={() => setNumbers([...numbers, numberInput])}
                >
                  +
                </Button>
                <Button
                  w="45px"
                  color="white"
                  colorPalette="red"
                  fontSize="20px"
                  marginStart="10px"
                  onClick={() => setNumbers([...numbers.slice(0, -1)])}
                >
                  -
                </Button>
              </Flex>
            </Flex>
            <Separator marginBottom="20px" />
            {numbers.map((item) => (
              <InputBox num={item} />
            ))}
          </Flex>

          {/* AGENTS AREA */}
          <Flex bg="gray.100" p="30px" direction="column">
            <Heading size="4xl" color="gray.600" paddingBottom="30px" textAlign='center'>
              Agent List
            </Heading>
            <Flex h="fit" flexWrap="wrap" p="40px" gap="30px" justify="center">
              {/* Agentes no editables */}
              {initialAgents.map((agent: Agent) => (
                <Flex
                  align="center"
                  justify="space-between"
                  width="100%"
                  borderBottom="1px solid #d4d4d8"
                  padding="15px 0"
                >
                  <Flex>
                    <InitialAgentBox agent={agent}></InitialAgentBox>
                    <Flex align="center" marginStart="20px">
                      {agent.function.map((id) => (
                        <Flex
                          bg="blue"
                          h="fit"
                          p="2px 6px"
                          borderRadius="10px"
                          marginEnd="10px"
                        >
                          <Heading fontSize="20px" color="white">
                            {
                              functionalities.find((func) => func.id === id)
                                ?.name
                            }
                          </Heading>
                        </Flex>
                      ))}
                    </Flex>
                  </Flex>
                  <Button
                    variant="outline"
                    color="green"
                    fontSize="25px"
                    onClick={() =>
                      setSelectedAgents([...selectedAgents, agent])
                    }
                  >
                    Add
                  </Button>
                </Flex>
              ))}

              {isLoading ? (
                <Heading>Cargando ...</Heading>
              ) : (
                agents.map((agent: Agent) => (
                  <Flex
                    align="center"
                    justify="space-between"
                    width="100%"
                    borderBottom="1px solid #d4d4d8"
                    padding="15px 0"
                  >
                    <Flex>
                      <AgentBox agent={agent}></AgentBox>
                      <Flex align="center" marginStart="20px">
                        {agent.function.map((id) => (
                          <Flex
                            bg="blue"
                            h="fit"
                            p="2px 6px"
                            borderRadius="10px"
                            marginEnd="10px"
                          >
                            <Heading fontSize="20px" color="white">
                              {
                                functionalities.find((func) => func.id === id)
                                  ?.name
                              }
                            </Heading>
                          </Flex>
                        ))}
                      </Flex>
                    </Flex>
                    <Flex>
                      <Button
                        variant="outline"
                        color="green"
                        marginEnd="10px"
                        fontSize="25px"
                        onClick={() =>
                          setSelectedAgents([...selectedAgents, agent])
                        }
                      >
                        Add
                      </Button>
                      <Button
                        variant="outline"
                        color="red"
                        fontSize="25px"
                        onClick={() => handleDeleteAgent(agent.name)}
                      >
                        Delete
                      </Button>
                    </Flex>
                  </Flex>
                ))
              )}
            </Flex>
          </Flex>

          {/* CODE AREA */}
          <Flex bg="gray.300" direction="column" p="30px" color="black">
            
            {/* HEAD */}
            <Heading
              size="4xl"
              h="fit"
              color="gray.600"
              paddingBottom="30px"
              textAlign="center"
            >
              Code
            </Heading>

            {/* AGENT NAME */}
            <Flex align="center" marginBottom="30px">
              <Heading color="gray.600" marginEnd="10px">
                Nombre:
              </Heading>
              <Input
                color="black"
                value={agentShow.name}
                onChange={(e) =>
                  setAgentShow({
                    id: agentShow.id,
                    name: e.target.value,
                    pythonCode: agentShow.pythonCode,
                    function: agentShow.function,
                    memory: agentShow.memory,
                    _type: agentShow._type,
                  })
                }
              />
            </Flex>

            {/* TAGS */}
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

            {/* CODE */}
            <Flex
              bg="white"
              borderRadius="20px"
              h="500px"
              direction="column"
              align="center"
              marginBottom="10px"
              overflowY='scroll'
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
                    border="none"
                    value={agentShow.pythonCode}
                    onChange={(e) =>
                      setAgentShow({
                        id: agentShow.id,
                        name: agentShow.name,
                        pythonCode: e.target.value,
                        function: agentShow.function,
                        memory: agentShow.memory,
                        _type: agentShow._type,
                      })
                    }
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
                    {initialAgents.some((e) => e.id == agent.id) &&
                      agent.id == 0 && <InitialAgentCode agent={agent} />}
                    {initialAgents.some((e) => e.id == agent.id) &&
                      agent.id == -1 && (
                        <InitialAgentCodeMemory
                          index={index}
                          agent={agent}
                          selectedAgents={selectedAgents}
                          setSelectedAgents={setSelectedAgents}
                        />
                      )}
                    {!initialAgents.some((e) => e.id == agent.id) && (
                      <AgentCode index={index} agent={agent} />
                    )}
                    <Button
                      variant="outline"
                      color="red"
                      fontSize="25px"
                      onClick={() =>
                        setSelectedAgents(
                          selectedAgents.filter((_, i) => i !== index)
                        )
                      }
                    >
                      X
                    </Button>
                  </Flex>
                ))
              )}
            </Flex>

            <MultiSelect
              options={functionalities.map((func) => ({
                label: func.name,
                value: func,
              }))}
              value={selectedValues}
              onChange={setSelectedValues}
              labelledBy="Select"
            />

            {/* BUTTONS */}
            <Flex margin="20px">
              {agentShow.id == 0 ? (
                <Button onClick={handleSubmitAgent}>Create Agent</Button>
              ) : (
                <Button variant='ghost'>Code</Button>
              )}
              {!isNativeCode && (
                <Button marginStart="10px" colorPalette="green" onClick={handleSolution}>
                  Run Solution
                </Button>
              )}
            </Flex>
          </Flex>

          {/* OUTPUT AREA */}
          <Flex bg="gray.100" direction="column" align="center" p="30px">
            <Heading size="4xl" color="gray.600" paddingBottom="30px">
              Output
            </Heading>
            <Separator marginBottom="20px" />
            {output.map((item) => (
              <InputBox num={item} />
            ))}
          </Flex>
        </Grid>
      </Flex>
    </>
  );
}

export default Home;
