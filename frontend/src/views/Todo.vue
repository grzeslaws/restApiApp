<template>
  <div>
    <table border=1>
      <tr>
        <td>id</td>
        <td>text</td>
        <td>complete</td>
        <td>user</td>
        <td>delete</td>
      </tr>
      <tr v-for="todo in todos">
        <td>{{todo.id}}</td>
        <td>{{todo.text}}</td>
        <td>{{todo.complete}}</td>
        <td>{{todo.user_id}}</td>
        <td><button @click="deleteTodoOnSubmit(todo.id)">x</button></td>
      </tr>
    </table>
    <div v-if="paginate.has_next" @click="refreshTodo(paginate.next)">next</div>
    <div v-if="paginate.has_prev" @click="refreshTodo(paginate.prev)">prev</div>
    <div>
      <span v-for="(item, index) in paginate.pages" @click="refreshTodo(index + 1)">{{ index + 1 }} | </span>
    </div>
    <form>
      <input v-model="text">
      <input type="checkbox" v-model="complete">
      <button @click="addTodoOnSubmit()" type="submit">Add</button>
    </form>
    <form>
      <input v-model="keywords">
      <button @click="searchOnSubmit()" type="submit">Search</button>
    </form>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import userService from "@/services/UserService.vue";

type Paginate = {
  has_prev: boolean;
  has_next: boolean;
  next: number | null;
  prev: number | null;
  page: number;
  pages: number;
};

@Component
export default class Todo extends Vue {
  todos: string[] = [];
  text = "";
  complete = false;
  todoProperty: any;
  keywords = "";
  paginate = {
    type: Object as () => Paginate
  };

  created() {
    this.refreshTodo();
  }

  refreshTodo(pageNumber = 1): PromiseLike<any> {
    return userService.getTodo(pageNumber).then(response => {
      this.todos = response.todos;
      this.paginate = response.paginate;
    });
  }

  deleteTodoOnSubmit(id: number) {
    userService.deleteTodo(id).then(() => {
      this.refreshTodo();
    });
  }

  addTodoOnSubmit() {
    const newTodo = {
      text: this.text,
      complete: this.complete
    };
    userService.addTodo(newTodo).then(() => {
      this.refreshTodo();
    });
  }

  searchOnSubmit() {
    this.$http.get(`search?keywords=${this.keywords}`);
  }
}
</script>
