import { Button, Flex, Heading, Input, NumberInput } from "@chakra-ui/react"
import { Agent } from "../../utils/types";

interface InitialAgentCodeProps {
    index:number;
    agent: Agent;
    selectedAgents: Agent[];
    setSelectedAgents: React.Dispatch<React.SetStateAction<Agent[]>>;
}

function InitialAgentCode({index,agent,selectedAgents,setSelectedAgents}:InitialAgentCodeProps) {


  return (
    <Button colorPalette='teal' h='fit' direction='column' p='10px' borderRadius='20px' w='190px' alignItems='center'>
        <Flex justifyContent='space-between' minW='fit'>
            <Heading fontSize='20px' color='white' alignContent='center'>{agent.name}</Heading>
            <Input type='number' marginStart='20px' min={0} padding='5px' border='1px solid white' h='30px' value={agent.memory} onChange={(e) => setSelectedAgents(selectedAgents.map((agent_array,i) =>
        i===index ? { ...agent_array, memory: parseInt(e.target.value) } : agent_array
      ))}/>
        </Flex>
    </Button>
  )
}

export default InitialAgentCode