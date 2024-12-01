import { Button, Flex, Heading, Input, NumberInput } from "@chakra-ui/react"
import { Agent } from "../../utils/types";

interface InitialAgentCodeProps {
    agent: Agent;
}

function InitialAgentCode({agent}:InitialAgentCodeProps) {


  return (
    <Button colorPalette='teal' h='fit' direction='column' p='10px' borderRadius='20px' w='190px' alignItems='center'>
        <Flex justifyContent='space-between' w='100%'>
            <Heading fontSize='20px' color='white' alignContent='center'>{agent.name}</Heading>
        </Flex>
    </Button>
  )
}

export default InitialAgentCode