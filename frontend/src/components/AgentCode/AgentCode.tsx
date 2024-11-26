import { Button, Flex, Heading } from "@chakra-ui/react"
import { Agent } from "../../utils/types";

interface AgentCodeProps {
    index: number;
    agent: Agent;
}

function AgentCode({index, agent}:AgentCodeProps) {

  return (
    <Button colorPalette='orange' h='fit' direction='column' p='10px' borderRadius='20px' w='150px'>
        <Flex justifyContent='space-between' w='100%'>
            <Heading fontSize='20px' color='white'>{agent.name}</Heading>
            <Heading fontSize='17px' color='white' bg='orange.800' borderRadius='20px' p='2px 10px'>2</Heading>
        </Flex>
    </Button>
  )
}

export default AgentCode