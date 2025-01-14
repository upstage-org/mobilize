
import userGraph from "./user";
import stageGraph from "./stage";
import configGraph from "./config";
import paymentGraph from "./payment";
import { createClient } from "./graphql";

const studioClient = createClient("studio_graphql");


export { studioClient, userGraph, stageGraph, configGraph, paymentGraph };