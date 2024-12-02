import { Button, Flex, Heading, Input } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import axios from "axios";
import FunctionalityBox from "../../components/FunctionalityBox/FunctionalityBox";
import { Functionality } from "../../utils/types";
import Navbar from "../../components/Navbar/Navbar";

function Facilities() {
  const [functionalities, setFunctionalities] = useState<Functionality[]>([]);
  const [input_functionality, setFunctionality] = useState<Functionality>({
    id: 0,
    name: "",
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchFunctionalities();
  }, []);

  // Función para obtener los agentes
  const fetchFunctionalities = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(
        "http://localhost:8000/appFunctionality/functionality/"
      ); // Reemplaza esta URL con la real de tu API
      setFunctionalities(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Función para obtener los agentes
  const fetchFunctionality = async (id: number) => {
    try {
      const response = await axios.get(
        `http://localhost:8000/appFunctionality/functionality/${id}`
      );
      setFunctionality(response.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFunctionality({ id: input_functionality.id, name: e.target.value });
    console.log(e.target.value);
  };

  const submitFunc = async () => {
    if (input_functionality.name == '') {
      alert('Las funcionalidades deben tener nombre');
    }

    if (input_functionality.id == 0) {
      try {
        await axios.post(
          `http://localhost:8000/appFunctionality/functionality/create/`,
          { name: input_functionality.name }
        );
      } catch (err) {
        console.error(err);
      }
    }
    else {
      try {
        await axios.put(
          `http://localhost:8000/appFunctionality/functionality/${input_functionality.id}`,
          { name: input_functionality.name }
        );
      } catch (err) {
        console.error(err);
      }
    }

    setFunctionality({id:0,name:''});
    fetchFunctionalities();
  };

  const deleteFunc = async (id:number) => {
    try {
      await axios.delete(
        `http://localhost:8000/appFunctionality/functionality/${id}`
      );
    } catch (err) {
      console.error(err);
    }

    fetchFunctionalities();
  };

  return (
    <>
      <Flex bg="gray.100" direction="column" h="100%">
        <Navbar />
        <Flex p="100px" direction="column">
          <Flex padding="30px 180px">
            <Input
              color="black"
              placeholder="Functionality name"
              value={input_functionality.name}
              onChange={handleInputChange}
            ></Input>
            <Button
              variant="outline"
              color="green"
              fontSize="25px"
              marginStart="20px"
              onClick={submitFunc}
            >
              Add
            </Button>
          </Flex>
          {isLoading ? (
            <Heading>Cargando ...</Heading>
          ) : (
            functionalities.map((functionality) => (
              <Flex
                align="center"
                justify="space-between"
                width="100%"
                borderBottom="1px solid #d4d4d8"
                padding="15px 0"
              >
                <FunctionalityBox name={functionality.name}></FunctionalityBox>
                <Flex>
                  <Button
                    variant="outline"
                    color="gray"
                    fontSize="25px"
                    onClick={() => fetchFunctionality(functionality.id)}
                  >
                    Edit
                  </Button>
                  <Button
                    variant="outline"
                    color="red"
                    fontSize="25px"
                    marginStart="20px"
                    onClick={() => deleteFunc(functionality.id)}
                  >
                    Delete
                  </Button>
                </Flex>
              </Flex>
            ))
          )}
        </Flex>
      </Flex>
    </>
  );
}

export default Facilities;
