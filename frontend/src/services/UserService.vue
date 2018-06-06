
<script lang="ts">
import { Vue } from "vue-property-decorator";

class UserService extends Vue {
  public getUsers(): PromiseLike<any> {
    return this.$http.get("user").then(response => response.json());
  }

  public getTodo(pageNumber: number): PromiseLike<any> {
    return this.$http.get(`todo/${pageNumber}`).then(response => response.json());
  }

  public addTodo(value: {}): PromiseLike<any> {
    const payload = value;
    return this.$http.post("todo", payload).then(response => response.json());
  }

  public deleteTodo(id: number): PromiseLike<any> {
    console.log(id)
    return this.$http.delete(`todo/${id}`).then(response => response.json());
  }
}

const userService = new UserService();
export default userService;
</script>