import { Button, Flex, Heading } from "@chakra-ui/react"
import { Agent } from "../../utils/types";

interface InitialAgentBoxProps {
    agent: Agent;
}

function InitialAgentBox({agent}:InitialAgentBoxProps) {


  return (
    <Button colorPalette='teal' h='fit' direction='column' p='10px' borderRadius='20px' w='150px'>
        <Flex justifyContent='space-between' w='100%'>
            <Heading fontSize='20px' color='white'>{agent.name}</Heading>
        </Flex>
    </Button>
  )
}

export default InitialAgentBox